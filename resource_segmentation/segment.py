from __future__ import annotations

from dataclasses import dataclass
from sys import maxsize
from typing import Generator, Generic, Iterator, cast

from .stream import Stream
from .types import P, Resource, Segment


def allocate_segments(
    resources_iter: Iterator[Resource[P]], border_incision: int, max_count: int
) -> Generator[Resource[P] | Segment[P], None, None]:
    segment = _collect_segment(
        stream=Stream(resources_iter),
        border_incision=border_incision,
        level=maxsize,
    )
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
class _Segment(Generic[P]):
    level: int
    count: int
    start_incision: int
    end_incision: int
    children: list[Resource[P] | _Segment[P]]


def _collect_segment(
    stream: Stream[Resource[P]], border_incision: int, level: int
) -> _Segment:
    start_incision: int = border_incision
    end_incision: int = border_incision
    children: list[Resource[P] | _Segment[P]] = []

    while True:
        resource = stream.get()
        if resource is None:
            break
        if len(children) == 0:  # is the first
            start_incision = resource.start_incision
            children.append(resource)
        else:
            pre_resource = children[-1]
            incision_level = _to_level(
                pre_resource.end_incision,
                resource.start_incision,
            )
            if incision_level > level:
                stream.recover(resource)
                end_incision = resource.end_incision
                break
            elif incision_level < level:
                stream.recover(resource)
                stream.recover(cast(Resource, pre_resource))
                segment = _collect_segment(
                    stream=stream,
                    border_incision=border_incision,
                    level=incision_level,
                )
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


def _split_segment_if_need(segment: _Segment[P], max_count: int):
    if segment.count <= max_count:
        yield segment
    else:
        count: int = 0
        children: list[Resource[P] | _Segment[P]] = []

        for item in _unfold_segments(segment, max_count):
            if len(children) > 0 and count + item.count > max_count:
                yield _create_segment(count, children, segment.level)
                count = 0
                children = []
            count += item.count
            children.append(item)

        if len(children) > 0:
            yield _create_segment(count, children, segment.level)


def _unfold_segments(
    segment: _Segment, max_count: int
) -> Generator[Resource[P] | _Segment[P]]:
    for item in segment.children:
        if item.count > max_count and isinstance(item, _Segment):
            for sub_item in _split_segment_if_need(item, max_count):
                yield sub_item
        else:
            yield item


def _create_segment(
    count: int, children: list[Resource[P] | _Segment[P]], level: int
) -> _Segment[P]:
    return _Segment(
        level=level,
        count=count,
        children=children,
        start_incision=children[0].start_incision,
        end_incision=children[-1].end_incision,
    )


def _deep_iter_segment(segment: _Segment[P]) -> Generator[Resource, None, None]:
    for child in segment.children:
        if isinstance(child, _Segment):
            yield from _deep_iter_segment(child)
        elif isinstance(child, Resource):
            yield child


def _to_level(left_incision: int, right_incision: int) -> int:
    return left_incision + right_incision
