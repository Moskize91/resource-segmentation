import unittest

from resource_segmentation.types import Resource, Group, Segment
from resource_segmentation.group import group_items
from resource_segmentation.segment import allocate_segments
from tests.common import Incision


class TestGroup(unittest.TestCase):
  def test_uniform_resources(self):
    resources = [
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 0),
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 1),
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 2),
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 3),
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 4),
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
        "body": ["T[0]100", "T[1]100"],
        "tail": ["T[2]100"],
        "tail_remain": 100,
      }, {
        "head": ["T[1]100"],
        "head_remain": 100,
        "body": ["T[2]100", "T[3]100"],
        "tail": ["T[4]100"],
        "tail_remain": 100,
      }, {
        "head": ["T[3]100"],
        "head_remain": 100,
        "body": ["T[4]100"],
        "tail": [],
        "tail_remain": 0,
      }],
    )

  def test_huge_fragment_barrier(self):
    resources = [
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 0),
      Resource(300, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 1),
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 2),
      Resource(100, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 3),
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
        "body": ["T[0]100"],
        "tail": ["T[1]300"],
        "tail_remain": 300,
      }, {
        "head": ["T[0]100"],
        "head_remain": 50,
        "body": ["T[1]300"],
        "tail": ["T[2]100"],
        "tail_remain": 50,
      }, {
        "head": ["T[1]300"],
        "head_remain": 200,
        "body": ["T[2]100", "T[3]100"],
        "tail": [],
        "tail_remain": 0,
      }],
    )

  def test_distribute_between_head_and_tail(self):
    resources = [
      Resource(400, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 0),
      Resource(200, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 1),
      Resource(400, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 2),
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
        "body": ["T[0]400"],
        "tail": [],
        "tail_remain": 0,
      }, {
        "head": ["T[0]400"],
        "head_remain": 40,
        "body": ["T[1]200"],
        "tail": ["T[2]400"],
        "tail_remain": 160,
      }, {
        "head": [],
        "head_remain": 0,
        "body": ["T[2]400"],
        "tail": [],
        "tail_remain": 0,
      }],
    )

  def test_distribute_all_to_tail(self):
    resources = [
      Resource(400, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 0),
      Resource(200, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 1),
      Resource(400, Incision.IMPOSSIBLE.value, Incision.IMPOSSIBLE.value, 2),
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
        "body": ["T[0]400"],
        "tail": [],
        "tail_remain": 0,
      }, {
        "head": [],
        "head_remain": 0,
        "body": ["T[1]200"],
        "tail": ["T[2]400"],
        "tail_remain": 200,
      }, {
        "head": [],
        "head_remain": 0,
        "body": ["T[2]400"],
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