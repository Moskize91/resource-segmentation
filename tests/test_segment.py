import unittest

from typing import Iterable
from resource_segmentation.segment import allocate_segments, Segment
from resource_segmentation.types import Resource, Incision


class TestSegment(unittest.TestCase):
  def test_no_segments(self):
    text_infos = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(text_infos, 100)),
      _to_json(text_infos),
    )

  def test_one_segment(self):
    text_infos = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(text_infos, 1000)),
      _to_json([
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          tokens=300,
          text_infos = [
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
    text_infos = [
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MUST_BE, 0),
      Resource(100, Incision.MUST_BE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(text_infos, 1000)),
      _to_json([
        Segment(
          tokens=200,
          text_infos = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
          ],
        ),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          tokens=200,
          text_infos = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MUST_BE, 0),
            Resource(100, Incision.MUST_BE, Incision.IMPOSSIBLE, 0),
          ],
        ),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      ]),
    )

  def test_forced_splitted_segments(self) -> None:
    text_infos = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(250, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(text_infos, 400)),
      _to_json([
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          tokens=200,
          text_infos = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
          ],
        ),
        Segment(
          tokens=350,
          text_infos = [
            Resource(250, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
          ],
        ),
        Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      ]),
    )

  def test_forced_splitted_segments_with_multi_levels(self) -> None:
    text_infos = [
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.MUST_BE, 0),
      Resource(100, Incision.MUST_BE, Incision.MOST_LIKELY, 0),
      Resource(100, Incision.MOST_LIKELY, Incision.IMPOSSIBLE, 0),
      Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
    ]
    self.assertEqual(
      _to_json(allocate_segments(text_infos, 300)),
      _to_json([
        Resource(100, Incision.IMPOSSIBLE, Incision.IMPOSSIBLE, 0),
        Segment(
          tokens=200,
          text_infos = [
            Resource(100, Incision.IMPOSSIBLE, Incision.MOST_LIKELY, 0),
            Resource(100, Incision.MOST_LIKELY, Incision.MOST_LIKELY, 0),
          ],
        ),
        Segment(
          tokens=300,
          text_infos = [
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
      json_list.append(_text_info_to_json(item))
    elif isinstance(item, Segment):
      json_list.append({
        "tokens": item.tokens,
        "text_infos": [_text_info_to_json(t) for t in item.text_infos],
      })
    else:
      raise ValueError(f"Unexpected: {item}")

  # print("# JSON List")
  # for i, item in enumerate(json_list):
  #   print(i, item)
  return json_list

def _text_info_to_json(text_info: Resource) -> list[dict]:
  return {
    "tokens": text_info.tokens,
    "start": text_info.start_incision.name,
    "end": text_info.end_incision.name,
  }