import unittest

from resource_segmentation.truncation import truncate_gap
from resource_segmentation.types import Group, Resource, Segment


class TestTruncation(unittest.TestCase):
    def test_no_truncation_needed(self):
        """当实际 count 等于 remain_count 时，不需要裁剪"""
        group = Group(
            head_remain_count=200,
            tail_remain_count=200,
            head=[Resource(100, 0, 0, 0), Resource(100, 0, 0, 1)],
            body=[Resource(400, 0, 0, 2)],
            tail=[Resource(100, 0, 0, 3), Resource(100, 0, 0, 4)],
        )

        result = truncate_gap(group)

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

    def test_truncate_tail_with_larger_remain_count(self):
        """tail_remain_count > 实际 count，从前往后保留（靠近 body）"""
        group = Group(
            head_remain_count=0,
            tail_remain_count=200,  # 建议保留 200，但实际只有 150
            head=[],
            body=[Resource(640, 0, 0, 0)],
            tail=[
                Resource(80, 0, 0, 1),
                Resource(70, 0, 0, 2),
            ],
        )

        result = truncate_gap(group)

        # tail 实际只有 150，小于 remain_count=200，所以保留全部
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 0,
                "tail_remain": 150,
                "head": [],
                "body": ["T[0]640"],
                "tail": ["T[1]80", "T[2]70"],
            },
        )

    def test_truncate_tail_with_smaller_remain_count(self):
        """tail_remain_count < 实际 count，从前往后保留（靠近 body）"""
        group = Group(
            head_remain_count=0,
            tail_remain_count=80,  # 只保留 80，实际有 150
            head=[],
            body=[Resource(640, 0, 0, 0)],
            tail=[
                Resource(80, 0, 0, 1),
                Resource(70, 0, 0, 2),
            ],
        )

        result = truncate_gap(group)

        # tail 从前往后保留 80，只能装第一个
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 0,
                "tail_remain": 80,
                "head": [],
                "body": ["T[0]640"],
                "tail": ["T[1]80"],
            },
        )

    def test_truncate_head_with_larger_remain_count(self):
        """head_remain_count > 实际 count，从后往前保留（靠近 body）"""
        group = Group(
            head_remain_count=200,  # 建议保留 200，但实际只有 150
            tail_remain_count=0,
            head=[
                Resource(80, 0, 0, 0),
                Resource(70, 0, 0, 1),
            ],
            body=[Resource(640, 0, 0, 2)],
            tail=[],
        )

        result = truncate_gap(group)

        # head 实际只有 150，小于 remain_count=200，所以保留全部
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 150,
                "tail_remain": 0,
                "head": ["T[0]80", "T[1]70"],
                "body": ["T[2]640"],
                "tail": [],
            },
        )

    def test_truncate_head_with_smaller_remain_count(self):
        """head_remain_count < 实际 count，从后往前保留（靠近 body）"""
        group = Group(
            head_remain_count=70,  # 只保留 70，实际有 150
            tail_remain_count=0,
            head=[
                Resource(80, 0, 0, 0),
                Resource(70, 0, 0, 1),
            ],
            body=[Resource(640, 0, 0, 2)],
            tail=[],
        )

        result = truncate_gap(group)

        # head 从后往前保留 70，只能装最后一个
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 70,
                "tail_remain": 0,
                "head": ["T[1]70"],
                "body": ["T[2]640"],
                "tail": [],
            },
        )

    def test_truncate_to_zero(self):
        """remain_count 为 0 时，清空 head/tail"""
        group = Group(
            head_remain_count=0,
            tail_remain_count=0,
            head=[Resource(100, 0, 0, 0)],
            body=[Resource(400, 0, 0, 1)],
            tail=[Resource(100, 0, 0, 2)],
        )

        result = truncate_gap(group)

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

    def test_truncate_segment_in_tail(self):
        """tail 包含 Segment，从前往后保留（靠近 body）"""
        group = Group(
            head_remain_count=0,
            tail_remain_count=80,  # 只保留 80，实际有 240
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

        result = truncate_gap(group)

        # tail 从前往后保留 80，只能装第一个 Resource
        self.assertEqual(
            _group_to_json(result),
            {
                "head_remain": 0,
                "tail_remain": 80,
                "head": [],
                "body": ["T[0]640"],
                "tail": ["T[1]80"],
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
