import unittest

from typing import Iterable
from resource_segmentation.segment import allocate_segments
from resource_segmentation.types import Resource, Segment


class TestSegment(unittest.TestCase):
  def test_no_segments(self):
    """测试：没有段生成 - 所有资源都保持独立"""
    resources = [
      Resource(100, 2, 2, 0),
      Resource(100, 2, 2, 0),
      Resource(100, 2, 2, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(iter(resources), 2, 100)),
      _to_json(resources),
    )

  def test_segments_due_to_size_limit(self):
    """测试：由于大小限制产生的段分割"""
    resources = [
      Resource(100, 2, 2, 0),
      Resource(100, 2, 1, 0),
      Resource(100, 1, 1, 0),
      Resource(100, 1, 2, 0),
      Resource(100, 2, 2, 0),
      Resource(100, 2, 2, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(iter(resources), 2, 400)),
      _to_json([
        Segment(
          count=400,
          resources=[
            Resource(100, 2, 2, 0),
            Resource(100, 2, 1, 0),
            Resource(100, 1, 1, 0),
            Resource(100, 1, 2, 0),
          ],
        ),
        Segment(
          count=200,
          resources=[
            Resource(100, 2, 2, 0),
            Resource(100, 2, 2, 0),
          ],
        ),
      ]),
    )

  def test_multiple_segments(self) -> None:
    """测试：生成多个段"""
    resources = [
      Resource(100, 2, 2, 0),
      Resource(100, 2, 1, 0),
      Resource(100, 1, 1, 0),
      Resource(100, 1, 2, 0),
      Resource(100, 2, 2, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(iter(resources), 2, 300)),
      _to_json([
        Resource(100, 2, 2, 0),
        Segment(
          count=300,
          resources=[
            Resource(100, 2, 1, 0),
            Resource(100, 1, 1, 0),
            Resource(100, 1, 2, 0),
          ],
        ),
        Resource(100, 2, 2, 0),
      ]),
    )

  def test_size_based_segmentation(self) -> None:
    """测试：基于大小的分段逻辑"""
    resources = [
      Resource(100, 2, 2, 0),
      Resource(100, 2, 1, 0),
      Resource(100, 1, 1, 0),
      Resource(250, 1, 1, 0),
      Resource(100, 1, 1, 0),
      Resource(100, 1, 2, 0),
      Resource(100, 2, 2, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(iter(resources), 2, 200)),
      _to_json([
        Resource(100, 2, 2, 0),
        Segment(
          count=200,
          resources=[
            Resource(100, 2, 1, 0),
            Resource(100, 1, 1, 0),
          ],
        ),
        Resource(250, 1, 1, 0),
        Segment(
          count=200,
          resources=[
            Resource(100, 1, 1, 0),
            Resource(100, 1, 2, 0),
          ],
        ),
        Resource(100, 2, 2, 0),
      ]),
    )

  def test_mixed_level_segmentation(self) -> None:
    """测试：混合级别 incision 的分段行为"""
    resources = [
      Resource(100, 2, 2, 0),
      Resource(100, 2, 1, 0),
      Resource(100, 1, 1, 0),
      Resource(100, 1, -1, 0),
      Resource(100, -1, 1, 0),
      Resource(100, 1, 2, 0),
      Resource(100, 2, 2, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(iter(resources), 2, 200)),
      _to_json([
        Resource(100, 2, 2, 0),
        Segment(
          count=200,
          resources=[
            Resource(100, 2, 1, 0),
            Resource(100, 1, 1, 0),
          ],
        ),
        Segment(
          count=200,
          resources=[
            Resource(100, 1, -1, 0),
            Resource(100, -1, 1, 0),
          ],
        ),
        Segment(
          count=200,
          resources=[
            Resource(100, 1, 2, 0),
            Resource(100, 2, 2, 0),
          ],
        ),
      ]),
    )

def _to_json(items: Iterable[Resource | Segment]) -> list[dict]:
  json_list: list[dict] = []
  for item in items:
    if isinstance(item, Resource):
      json_list.append(_resource_to_json(item))
    elif isinstance(item, Segment):
      json_list.append({
        "count": item.count,
        "resources": [_resource_to_json(t) for t in item.resources],
      })
    else:
      raise ValueError(f"Unexpected: {item}")

  return json_list

def _resource_to_json(resource: Resource) -> dict:
  return {
    "count": resource.count,
    "start": resource.start_incision,
    "end": resource.end_incision,
  }