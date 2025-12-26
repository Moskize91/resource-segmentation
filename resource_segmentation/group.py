from __future__ import annotations

from dataclasses import dataclass
from math import floor
from typing import Generator, Generic, Iterator

from .stream import Stream
from .types import Group, P, Resource, Segment


def group_items(
    items_iter: Iterator[Resource[P] | Segment],
    max_count: int,
    gap_rate: float,
    tail_rate: float,
) -> Generator[Group[P], None, None]:
    gap_max_count = floor(max_count * gap_rate)
    assert gap_max_count >= 0

    curr_group: _Group[P] = _Group(
        _Attributes(
            max_count=max_count,
            gap_max_count=gap_max_count,
            tail_rate=tail_rate,
        )
    )
    curr_group.head.seal()
    stream: Stream[_Item] = Stream(items_iter)

    while True:
        item = stream.get()
        if item is not None:
            success = curr_group.append(item)
            if success:
                continue

        if curr_group.body.has_any:
            yield curr_group.report()
        if item is not None:
            stream.recover(item)
        for tail_item in reversed(list(curr_group.tail)):
            stream.recover(tail_item)

        if not stream.has_buffer and item is None:
            # next item never comes
            break
        curr_group = curr_group.next()


_Item = Resource[P] | Segment[P]


@dataclass
class _Attributes:
    max_count: int
    gap_max_count: int
    tail_rate: float


class _Group(Generic[P]):
    def __init__(self, attr: _Attributes):
        self._attr: _Attributes = attr
        body_max_count = attr.max_count - attr.gap_max_count * 2
        assert body_max_count > 0

        self.head: _Buffer = _Buffer(attr.gap_max_count)
        self.tail: _Buffer = _Buffer(attr.gap_max_count)
        self.body: _Buffer = _Buffer(body_max_count)

    def append(self, item: _Item) -> bool:
        success: bool = False
        for buffer in (self.head, self.body, self.tail):
            if buffer.is_sealed:
                continue
            if not buffer.can_append(item):
                buffer.seal()
                continue
            buffer.append(item)
            success = True
            break
        return success

    def next(self) -> _Group[P]:
        next_group: _Group[P] = _Group(self._attr)
        next_head = next_group.head
        for item in reversed([*self.head, *self.body]):
            if next_head.can_append(item):
                next_head.append(item)
            else:
                next_head.reverse().seal()
                break
        return next_group

    def report(self) -> Group[P]:
        count: int = 0
        for buffer in (self.head, self.body, self.tail):
            count += buffer.count

        head_remain_count = self.head.count
        tail_remain_count = self.tail.count

        if count > self._attr.max_count:
            if self.body.count > self._attr.max_count:
                head_remain_count = 0
                tail_remain_count = 0
            else:
                tail_rate = self._attr.tail_rate
                remain_count = self._attr.max_count - self.body.count
                if self.head.count < remain_count * (1.0 - tail_rate):
                    tail_remain_count = remain_count - self.head.count
                elif self.tail.count < remain_count * tail_rate:
                    head_remain_count = remain_count - self.tail.count
                else:
                    head_remain_count = round(remain_count * (1.0 - tail_rate))
                    tail_remain_count = round(remain_count * tail_rate)

        head = list(self.head)
        tail = list(self.tail)

        if head_remain_count == 0:
            head = []
        if tail_remain_count == 0:
            tail = []

        return Group(
            head_remain_count=head_remain_count,
            tail_remain_count=tail_remain_count,
            head=head,
            body=list(self.body),
            tail=tail,
        )


class _Buffer:
    def __init__(self, max_count: int):
        self._max_count: int = max_count
        self._items: list[_Item] = []
        self._count: int = 0
        self._is_sealed: bool = False

    @property
    def is_sealed(self) -> bool:
        return self._is_sealed

    @property
    def has_any(self) -> bool:
        return len(self._items) > 0

    @property
    def count(self) -> int:
        return self._count

    def seal(self):
        self._is_sealed = True

    def reverse(self) -> _Buffer:
        self._items.reverse()
        return self

    def __iter__(self):
        return iter(self._items)

    def append(self, item: _Item):
        self._items.append(item)
        self._count += item.count

    def can_append(self, item: _Item) -> bool:
        if self._is_sealed:
            return False
        if len(self._items) == 0:
            return True
        next_count = self._count + item.count
        return next_count <= self._max_count
