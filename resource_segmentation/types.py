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
  tokens: int
  start_incision: Incision
  end_incision: Incision
  payload: P