import unittest

from resource_segmentation.types import Resource, Group, Segment
from resource_segmentation.group import group_items
from resource_segmentation.segment import allocate_segments
from tests.common import Incision


class TestGroup(unittest.TestCase):
  def test_uniform_resources(self):
    resources = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 1),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 2),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 3),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 4),
    ]
    groups = list(group_items(
      items_iter=allocate_segments(iter(resources), Incision.IMPOSSIBLE, 1000),
      max_count=400,
      gap_rate=0.25,
      tail_rate=0.5,
    ))
    self.assertListEqual(
      [_group_to_json(group) for group in groups],
      [{
        "head": [],
        "head_remain": 0,
        "body": ["S[]500"],
        "tail": [],
        "tail_remain": 0,
      }],
    )

  def test_huge_fragment_barrier(self):
    resources = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(300, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 1),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 2),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 3),
    ]
    groups = list(group_items(
      items_iter=allocate_segments(iter(resources), Incision.IMPOSSIBLE, 1000),
      max_count=400,
      gap_rate=0.25,
      tail_rate=0.5,
    ))
    self.assertListEqual(
      [_group_to_json(group) for group in groups],
      [{
        "head": [],
        "head_remain": 0,
        "body": ["S[]600"],
        "tail": [],
        "tail_remain": 0,
      }],
    )

  def test_distribute_between_head_and_tail(self):
    resources = [
      Resource(400, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(200, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 1),
      Resource(400, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 2),
    ]
    groups = list(group_items(
      items_iter=allocate_segments(iter(resources), Incision.IMPOSSIBLE, 1000),
      max_count=400,
      gap_rate=0.25,
      tail_rate=0.8,
    ))
    self.assertListEqual(
      [_group_to_json(group) for group in groups],
      [{
        "head": [],
        "head_remain": 0,
        "body": ["S[]1000"],
        "tail": [],
        "tail_remain": 0,
      }],
    )

  def test_distribute_all_to_tail(self):
    resources = [
      Resource(400, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(200, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 1),
      Resource(400, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 2),
    ]
    groups = list(group_items(
      items_iter=allocate_segments(iter(resources), Incision.IMPOSSIBLE, 1000),
      max_count=400,
      gap_rate=0.25,
      tail_rate=1.0,
    ))
    self.assertListEqual(
      [_group_to_json(group) for group in groups],
      [{
        "head": [],
        "head_remain": 0,
        "body": ["S[]1000"],
        "tail": [],
        "tail_remain": 0,
      }],
    )

def _group_to_json(item: Group) -> dict:
  return {
    "head_remain": item.head_remain_count,
    "tail_remain": item.tail_remain_count,
    "head": [_item_to_json(item) for item in item.head],
    "body": [_item_to_json(item) for item in item.body],
    "tail": [_item_to_json(item) for item in item.tail],
  }

def _item_to_json(item: Resource | Segment) -> str:
  if isinstance(item, Resource):
    return f"T[{item.payload}]{item.count}"
  else:
    return f"S[]{item.count}"