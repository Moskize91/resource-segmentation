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
class Segment:
  count: int
  resources: list[Resource]

@dataclass
class Group:
  head_remain_count: int
  tail_remain_count: int
  head: list[Resource | Segment]
  body: list[Resource | Segment]
  tail: list[Resource | Segment]