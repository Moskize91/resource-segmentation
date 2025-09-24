from enum import IntEnum


class Incision(IntEnum):
  MUST_BE = 2
  MOST_LIKELY = 1
  UNCERTAIN = 0
  IMPOSSIBLE = -1