from dataclasses import dataclass
from enum import IntEnum
from typing import TypeVar, Generic


P = TypeVar("P")

@dataclass
class Incision(IntEnum):
  MUST_BE = 2
  MOST_LIKELY = 1
  IMPOSSIBLE = -1
  UNCERTAIN = 0

@dataclass
class Resource(Generic[P]):
  count: int
  start_incision: Incision
  end_incision: Incision
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