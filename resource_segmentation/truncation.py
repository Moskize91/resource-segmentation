"""Truncate head and tail to respect gap_max_count limits."""

from __future__ import annotations

from .types import Group, P, Resource, Segment


def truncate_gap(group: Group[P], gap_max_count: int) -> Group[P]:
    """
    Truncate group's head and tail to respect gap_max_count limit.

    This function ensures that head and tail don't exceed gap_max_count
    by extracting only the necessary resources.

    Args:
        group: The group to truncate
        gap_max_count: Maximum count allowed for head/tail

    Returns:
        A new group with truncated head and tail
    """
    truncated_head = _truncate_items(group.head, gap_max_count, from_start=True)
    truncated_tail = _truncate_items(group.tail, gap_max_count, from_start=False)

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


def _truncate_items(
    items: list[Resource[P] | Segment[P]], target_count: int, from_start: bool
) -> list[Resource[P] | Segment[P]]:
    """
    Truncate items to match target_count.

    Args:
        items: List of resources or segments
        target_count: Target total count
        from_start: If True, keep items from start; if False, keep items from end

    Returns:
        Truncated list of items
    """
    if target_count == 0:
        return []

    if from_start:
        return _truncate_from_start(items, target_count)
    else:
        return _truncate_from_end(items, target_count)


def _truncate_from_start(
    items: list[Resource[P] | Segment[P]], target_count: int
) -> list[Resource[P] | Segment[P]]:
    """Truncate items keeping the start (for head)"""
    current_count = 0
    result: list[Resource[P] | Segment[P]] = []

    for item in items:
        if current_count >= target_count:
            break

        remaining = target_count - current_count

        if item.count <= remaining:
            # Item fits completely
            result.append(item)
            current_count += item.count
        else:
            # Need to truncate this item
            if isinstance(item, Segment):
                # Truncate segment by extracting resources from start
                truncated_resources = _extract_resources_from_start(
                    item.resources, remaining
                )
                if len(truncated_resources) == 1:
                    result.append(truncated_resources[0])
                else:
                    result.append(
                        Segment(
                            count=sum(r.count for r in truncated_resources),
                            resources=truncated_resources,
                        )
                    )
                current_count += sum(r.count for r in truncated_resources)
            else:
                # Resource itself is too large, stop here
                break

    return result


def _truncate_from_end(
    items: list[Resource[P] | Segment[P]], target_count: int
) -> list[Resource[P] | Segment[P]]:
    """Truncate items keeping the end (for tail)"""
    current_count = 0
    result: list[Resource[P] | Segment[P]] = []

    # Process items in reverse order
    for item in reversed(items):
        if current_count >= target_count:
            break

        remaining = target_count - current_count

        if item.count <= remaining:
            # Item fits completely
            result.insert(0, item)  # Insert at front to maintain order
            current_count += item.count
        else:
            # Need to truncate this item
            if isinstance(item, Segment):
                # Truncate segment by extracting resources from end
                truncated_resources = _extract_resources_from_end(
                    item.resources, remaining
                )
                if len(truncated_resources) == 1:
                    result.insert(0, truncated_resources[0])
                else:
                    result.insert(
                        0,
                        Segment(
                            count=sum(r.count for r in truncated_resources),
                            resources=truncated_resources,
                        ),
                    )
                current_count += sum(r.count for r in truncated_resources)
            else:
                # Resource itself is too large, stop here
                break

    return result


def _extract_resources_from_start(
    resources: list[Resource[P]], target_count: int
) -> list[Resource[P]]:
    """Extract resources from start up to target_count"""
    current_count = 0
    result: list[Resource[P]] = []

    for resource in resources:
        if current_count >= target_count:
            break

        if current_count + resource.count <= target_count:
            result.append(resource)
            current_count += resource.count
        else:
            break

    return result


def _extract_resources_from_end(
    resources: list[Resource[P]], target_count: int
) -> list[Resource[P]]:
    """Extract resources from end up to target_count"""
    current_count = 0
    result: list[Resource[P]] = []

    for resource in reversed(resources):
        if current_count >= target_count:
            break

        if current_count + resource.count <= target_count:
            result.insert(0, resource)  # Insert at front to maintain order
            current_count += resource.count
        else:
            break

    return result
