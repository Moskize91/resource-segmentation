from dataclasses import dataclass
from typing import Generic, TypeVar

P = TypeVar("P")


@dataclass
class Resource(Generic[P]):
    count: int
    start_incision: int
    end_incision: int
    payload: P


@dataclass
class Segment(Generic[P]):
    count: int
    resources: list[Resource[P]]


@dataclass
class Group(Generic[P]):
    head_remain_count: int
    tail_remain_count: int
    head: list[Resource[P] | Segment[P]]
    body: list[Resource[P] | Segment[P]]
    tail: list[Resource[P] | Segment[P]]
