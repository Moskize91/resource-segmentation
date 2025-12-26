from typing import cast

from .types import Group, P, Resource, Segment


def truncate_gap(group: Group[P]) -> Group[P]:
    truncated_head = _truncate_group_parts(
        parts=group.head,
        remain_count=group.head_remain_count,
        remain_head=False,
    )
    truncated_tail = _truncate_group_parts(
        parts=group.tail,
        remain_count=group.tail_remain_count,
        remain_head=True,
    )

    # Recalculate remain counts after truncation
    head_remain_count = sum(item.count for item in truncated_head)
    tail_remain_count = sum(item.count for item in truncated_tail)

    return Group(
        head_remain_count=head_remain_count,
        tail_remain_count=tail_remain_count,
        head=truncated_head,
        body=group.body,
        tail=truncated_tail,
    )


def _truncate_group_parts(
    parts: list[Resource[P] | Segment[P]],
    remain_count: int,
    remain_head: bool,
) -> list[Resource[P] | Segment[P]]:
    truncated: list[Resource[P] | Segment[P]] = []

    for part in parts if remain_head else reversed(parts):
        if remain_count <= 0:
            break
        if isinstance(part, Resource):
            truncated.append(part)
            remain_count -= part.count
        elif isinstance(part, Segment):
            truncated_resources = _truncate_resources(
                resources=part.resources,
                remain_count=remain_count,
                remain_head=remain_head,
            )
            truncated_segment: Segment[P] = Segment(
                count=sum(r.count for r in truncated_resources),
                resources=truncated_resources,
            )
            truncated.append(truncated_segment)
            remain_count -= truncated_segment.count

    if not remain_head:
        truncated.reverse()

    if len(truncated) == 1 and isinstance(truncated[0], Segment):
        return cast(list[Resource[P] | Segment[P]], truncated[0].resources)
    else:
        return truncated


def _truncate_resources(
    resources: list[Resource[P]],
    remain_count: int,
    remain_head: bool,
) -> list[Resource[P]]:
    truncated: list[Resource[P]] = []
    for resource in resources if remain_head else reversed(resources):
        if remain_count <= 0:
            break
        truncated.append(resource)
        remain_count -= resource.count
    if not remain_head:
        truncated.reverse()
    return truncated
