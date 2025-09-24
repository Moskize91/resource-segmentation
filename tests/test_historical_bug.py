import unittest
from resource_segmentation import split, Resource
from resource_segmentation.types import Segment


class TestHistoricalBug(unittest.TestCase):
  def test_sentence_segmentation_bug(self):
    resources = [
      Resource(26, 2, 1, "This is the first sentence"),
      Resource(1, 1, 2, "."),
      Resource(27, 2, 1, "This is the second sentence"),
      Resource(1, 1, 2, "."),
    ]

    groups = list(split(
      iter(resources),
      max_segment_count=30,
      border_incision=1,
      gap_rate=0.0,
      tail_rate=0.0
    ))
    result_texts = []

    for group in groups:
      for item in group.body:
        if isinstance(item, Segment):
          text = "".join(r.payload for r in item.resources)
          result_texts.append(text)
        else:  # Resource
          text = item.payload
          result_texts.append(text)

    self.assertEqual(result_texts, [
      "This is the first sentence",
      ".This is the second sentence.",
    ])