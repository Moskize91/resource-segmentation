import unittest

from resource_segmentation.truncation import truncate_gap
from resource_segmentation.types import Group, Resource, Segment


class TestTruncation(unittest.TestCase):
    def test_no_truncation_needed(self):
        """当 head/tail 不超过 gap_max_count 时，不需要裁剪"""
        group = Group(
            head_remain_count=200,
            tail_remain_count=200,
            head=[Resource(100, 0, 0, 0), Resource(100, 0, 0, 1)],
            body=[Resource(400, 0, 0, 2)],
            tail=[Resource(100, 0, 0, 3), Resource(100, 0, 0, 4)],
        )

        result = truncate_gap(group, gap_max_count=200)

        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 200,
                "tail_remain": 200,
                "head": ["T[0]100", "T[1]100"],
                "body": ["T[2]400"],
                "tail": ["T[3]100", "T[4]100"],
            },
        )

    def test_truncate_tail_from_end(self):
        """裁剪 tail 中的 Segment，从后往前保留"""
        group = Group(
            head_remain_count=0,
            tail_remain_count=320,
            head=[],
            body=[Resource(640, 0, 0, 0)],
            tail=[
                Segment(
                    count=320,
                    resources=[
                        Resource(80, 0, 0, 1),
                        Resource(80, 0, 0, 2),
                        Resource(80, 0, 0, 3),
                        Resource(80, 0, 0, 4),
                    ],
                )
            ],
        )

        result = truncate_gap(group, gap_max_count=150)

        # tail 从后往前保留 150 tokens (最后 1 个 80)
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 0,
                "tail_remain": 80,
                "head": [],
                "body": ["T[0]640"],
                "tail": ["T[4]80"],
            },
        )

    def test_truncate_head_from_start(self):
        """裁剪 head，从前往后保留"""
        group = Group(
            head_remain_count=320,
            tail_remain_count=0,
            head=[
                Segment(
                    count=320,
                    resources=[
                        Resource(80, 0, 0, 0),
                        Resource(80, 0, 0, 1),
                        Resource(80, 0, 0, 2),
                        Resource(80, 0, 0, 3),
                    ],
                )
            ],
            body=[Resource(640, 0, 0, 4)],
            tail=[],
        )

        result = truncate_gap(group, gap_max_count=150)

        # head 从前往后保留 150 tokens (前 1 个 80)
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 80,
                "tail_remain": 0,
                "head": ["T[0]80"],
                "body": ["T[4]640"],
                "tail": [],
            },
        )

    def test_truncate_to_zero(self):
        """gap_max_count 为 0 时，清空 head/tail"""
        group = Group(
            head_remain_count=100,
            tail_remain_count=100,
            head=[Resource(100, 0, 0, 0)],
            body=[Resource(400, 0, 0, 1)],
            tail=[Resource(100, 0, 0, 2)],
        )

        result = truncate_gap(group, gap_max_count=0)

        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 0,
                "tail_remain": 0,
                "head": [],
                "body": ["T[1]400"],
                "tail": [],
            },
        )

    def test_truncate_tail_multiple_resources(self):
        """tail 包含多个 resources，从后往前保留"""
        group = Group(
            head_remain_count=0,
            tail_remain_count=240,
            head=[],
            body=[Resource(640, 0, 0, 0)],
            tail=[
                Segment(
                    count=240,
                    resources=[
                        Resource(80, 0, 0, 1),
                        Resource(80, 0, 0, 2),
                        Resource(80, 0, 0, 3),
                    ],
                )
            ],
        )

        result = truncate_gap(group, gap_max_count=150)

        # tail 从后往前保留 150 tokens (最后 1 个 80)
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 0,
                "tail_remain": 80,
                "head": [],
                "body": ["T[0]640"],
                "tail": ["T[3]80"],
            },
        )


def _group_to_json(group: Group) -> dict:
    """Convert a Group to a JSON-like dict for snapshot testing."""
    return {
        "head_remain": group.head_remain_count,
        "tail_remain": group.tail_remain_count,
        "head": [_item_to_json(item) for item in group.head],
        "body": [_item_to_json(item) for item in group.body],
        "tail": [_item_to_json(item) for item in group.tail],
    }


def _item_to_json(item: Resource | Segment) -> str:
    """Convert a Resource or Segment to a string representation."""
    if isinstance(item, Resource):
        return f"T[{item.payload}]{item.count}"
    else:  # Segment
        return f"S[]{item.count}"
