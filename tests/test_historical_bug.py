import unittest

from resource_segmentation import Resource, split
from resource_segmentation.types import Segment


class TestHistoricalBug(unittest.TestCase):
    def test_sentence_segmentation_bug(self):
        resources = [
            Resource(26, 2, 1, "This is the first sentence"),
            Resource(1, 1, 2, "."),
            Resource(27, 2, 1, "This is the second sentence"),
            Resource(1, 1, 2, "."),
        ]

        groups = list(
            split(
                iter(resources),
                max_segment_count=30,
                border_incision=1,
                gap_rate=0.0,
                tail_rate=0.0,
            )
        )
        result_texts = []

        for group in groups:
            for item in group.body:
                if isinstance(item, Segment):
                    text = "".join(r.payload for r in item.resources)
                    result_texts.append(text)
                else:  # Resource
                    text = item.payload
                    result_texts.append(text)

        self.assertEqual(
            result_texts,
            [
                "This is the first sentence.",
                "This is the second sentence.",
            ],
        )

    def test_equal_incision_with_gap_rate(self):
        """
        Bug: 当所有 Resource 的 incision 相等时，allocate_segments 会把它们合并成大 Segment，
        按 max_count 拆分。但 grouping 阶段的 body_max_count = max_count - gap_max_count * 2，
        导致 Segment 可能超出 body 的容量限制。

        修复：allocate_segments 应该按 body_max_count 拆分 Segment，而不是 max_count。
        """
        resources = [
            Resource(count=80, start_incision=0, end_incision=0, payload=i)
            for i in range(12)
        ]
        groups = list(
            split(
                resources=iter(resources),
                max_segment_count=1000,
                border_incision=0,
                gap_rate=0.15,
                tail_rate=0.5,
            )
        )

        def extract_resource_counts(
            items: list[Segment[int] | Resource[int]] | list[Resource[int]],
        ) -> list[int]:
            counts = []
            for item in items:
                if isinstance(item, Segment):
                    counts.extend(extract_resource_counts(item.resources))
                else:  # Resource
                    counts.append(item.count)
            return counts

        def group_to_counts(group) -> tuple[list[int], list[int], list[int]]:
            return (
                extract_resource_counts(group.head),
                extract_resource_counts(group.body),
                extract_resource_counts(group.tail),
            )

        self.assertEqual(
            [group_to_counts(g) for g in groups],
            [
                ([], [80] * 8, [80] * 4),  # Group 0: body=640, tail=320
                ([80] * 8, [80] * 4, []),  # Group 1: head=640, body=320
            ],
        )
