import unittest

from typing import Iterable
from resource_segmentation.segment import allocate_segments
from resource_segmentation.types import Resource, Incision, Segment


class TestSegment(unittest.TestCase):
  def test_no_segments(self):
    resources = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(resources, 100)),
      _to_json(resources),
    )

  def test_one_segment(self):
    resources = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(resources, 1000)),
      _to_json([
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          count=300,
          resources = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
          ],
        ),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      ]),
    )

  def test_2_segments(self) -> None:
    resources = [
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MUST_BE, 0),
      Resource(100, Incision.MUST_BE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(resources, 1000)),
      _to_json([
        Segment(
          count=200,
          resources = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
          ],
        ),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          count=200,
          resources = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MUST_BE, 0),
            Resource(100, Incision.MUST_BE, Incision.IMPOSSIBLE, 0),
          ],
        ),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      ]),
    )

  def test_forced_splitted_segments(self) -> None:
    resources = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(250, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(resources, 400)),
      _to_json([
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          count=200,
          resources = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
          ],
        ),
        Segment(
          count=350,
          resources = [
            Resource(250, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
          ],
        ),
        Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      ]),
    )

  def test_forced_splitted_segments_with_multi_levels(self) -> None:
    resources = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MUST_BE, 0),
      Resource(100, Incision.MUST_BE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(resources, 300)),
      _to_json([
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          count=200,
          resources = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
          ],
        ),
        Segment(
          count=300,
          resources = [
            Resource(100, Incision.MOST_LIKELY, Incision.MUST_BE, 0),
            Resource(100, Incision.MUST_BE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
          ],
        ),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
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

  # print("# JSON List")
  # for i, item in enumerate(json_list):
  #   print(i, item)
  return json_list

def _resource_to_json(resource: Resource) -> list[dict]:
  return {
    "count": resource.count,
    "start": resource.start_incision.name,
    "end": resource.end_incision.name,
  }