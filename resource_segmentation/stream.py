from typing import Generic, Iterator, TypeVar

E = TypeVar("E")


class Stream(Generic[E]):
    def __init__(self, elements_iter: Iterator[E]):
        self._iterator: Iterator[E] = elements_iter
        self._buffer: list[E] = []

    @property
    def has_buffer(self) -> bool:
        return len(self._buffer) > 0

    def recover(self, element: E):
        self._buffer.append(element)

    def get(self) -> E | None:
        if len(self._buffer) > 0:
            return self._buffer.pop()
        else:
            return next(self._iterator, None)
