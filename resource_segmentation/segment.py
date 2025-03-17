from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Generator
from .types import Resource, Incision
from .stream import Stream


_MIN_LEVEL = -1

@dataclass
class Segment:
  count: int
  resources: list[Resource]

def allocate_segments(resources: Iterable[Resource], max_count: int) -> Generator[Resource | Segment, None, None]:
  segment = _collect_segment(Stream(resources), _MIN_LEVEL)
  for item in segment.children:
    if isinstance(item, _Segment):
      for segment in _split_segment_if_need(item, max_count):
        yield _transform_segment(segment)
    elif isinstance(item, Resource):
      yield item

def _transform_segment(segment: _Segment):
  children = list(_deep_iter_segment(segment))
  if len(children) == 1:
    return children[0]
  else:
    return Segment(
      count=segment.count,
      resources=children,
    )

@dataclass
class _Segment:
  level: int
  count: int
  start_incision: Incision
  end_incision: Incision
  children: list[Resource | _Segment]

def _collect_segment(stream: Stream[Resource], level: int) -> _Segment:
  start_incision: Incision = Incision.IMPOSSIBLE
  end_incision: Incision = Incision.IMPOSSIBLE
  children: list[Resource | _Segment] = []

  while True:
    resource = stream.get()
    if resource is None:
      break
    if len(children) == 0: # is the first
      start_incision = resource.start_incision
      children.append(resource)
    else:
      pre_resource = children[-1]
      incision_level = _to_level(
        pre_resource.end_incision,
        resource.start_incision,
      )
      if incision_level < level:
        stream.recover(resource)
        end_incision = resource.end_incision
        break
      elif incision_level > level:
        stream.recover(resource)
        stream.recover(pre_resource)
        segment = _collect_segment(stream, incision_level)
        children[-1] = segment
      else:
        children.append(resource)

  count: int = 0
  for child in children:
    count += child.count

  return _Segment(
    level=level,
    count=count,
    start_incision=start_incision,
    end_incision=end_incision,
    children=children,
  )

def _split_segment_if_need(segment: _Segment, max_count: int):
  if segment.count <= max_count:
    yield segment
  else:
    count: int = 0
    children: list[Resource | _Segment] = []

    for item in _unfold_segments(segment, max_count):
      if len(children) > 0 and count + item.count > max_count:
        yield _create_segment(count, children, segment.level)
        count = 0
        children = []
      count += item.count
      children.append(item)

    if len(children) > 0:
      yield _create_segment(count, children, segment.level)

def _unfold_segments(segment: _Segment, max_count: int) -> Generator[Resource | _Segment]:
  for item in segment.children:
    if item.count > max_count and isinstance(item, _Segment):
      for sub_item in _split_segment_if_need(item, max_count):
        yield sub_item
    else:
      yield item

def _create_segment(count: int, children: list[Resource | _Segment], level: int) -> _Segment:
  return _Segment(
    level=level,
    count=count,
    children=children,
    start_incision=children[0].start_incision,
    end_incision=children[-1].end_incision,
  )

def _deep_iter_segment(segment: _Segment) -> Generator[Resource, None, None]:
  for child in segment.children:
    if isinstance(child, _Segment):
      yield from _deep_iter_segment(child)
    elif isinstance(child, Resource):
      yield child

def _to_level(left_incision: Incision, right_incision: Incision) -> int:
  return max(_MIN_LEVEL, left_incision.value + right_incision.value)
