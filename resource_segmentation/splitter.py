from typing import Iterator, Generator
from .types import P, Resource, Group
from .group import group_items
from .segment import allocate_segments


def split(
    resources: Iterator[Resource[P]],
    max_segment_count: int,
    gap_rate: float = 0.0,
    tail_rate: float = 0.5,
  ) -> Generator[Group[P], None, None]:
  """Group resources.

  This method groups `resources`, where `max_segment_count` limits the cumulative quantity (represented by `Resource.token`) for each group.
  Additionally, if `gap_rate` is not 0, it will leave an overlapping portion between groups. In this case, `tail_rate` is used to determine whether the overlapping portion is concentrated at the front or back of the group.

  This method reads the contents of `resources` in a streaming manner and outputs each group as a Generator.

  Args:
    resources (Iterator[Resource]): The collection of resources to be grouped.
    gap_rate (float): A value between 0.0 and 1.0, representing the proportion of overlapping quantity between groups relative to the total.
    tail_rate (float): A value between 0.0 and 1.0, representing the proportion of the overlapping portion concentrated at the tail. For an even distribution, use 0.5.
    max_segment_count (int): The maximum number of resource segments.

  Yields:
    Generator[Group, None, None]: A generator yielding grouped resource sets. Each group is a `Group` object.
  """
  yield from group_items(
    max_count=max_segment_count,
    gap_rate=gap_rate,
    tail_rate=tail_rate,
    items_iter=allocate_segments(
      resources_iter=resources,
      max_count=max_segment_count,
    ),
  )