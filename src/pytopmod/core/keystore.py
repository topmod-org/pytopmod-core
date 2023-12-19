import collections
from typing import Generic, Iterator, TypeVar, cast

K = TypeVar("K", bound=str)


class KeyStore(Generic[K]):
    """Convenience class to generate and store simple human-readable object keys.

    This is used to handle simple object keys (e.g 'v1', 'v2' for vertices) to
    simplify code verification with literature.

    The caller provides a key prefix (e.g 'v') and an optional key index offset
    (by default 1 so keys start at e.g 'v1' instead of 'v0'), and uses the new()
    and delete() methods to create/delete keys.

    Also provides iteration and membership check (__iter__ and __contains__) and
    typed keys (e.g via TypeAliases).

    Internally, the keys are maintained in a collections.Counter which remembers
    the order in which items were added for testing reproductibility (vs. a set).
    """

    def __init__(self, key_prefix: str, key_index_offset: int = 1):
        self._key_prefix = key_prefix
        self._key_index_offset = key_index_offset
        self._counter = collections.Counter[K]()

    def __iter__(self) -> Iterator[K]:
        return self._counter.elements()

    def __contains__(self, key: K) -> bool:
        return self._counter[key] > 0

    def __repr__(self) -> str:
        return list(self.__iter__()).__repr__()

    def __len__(self) -> int:
        return self._counter.total()

    def new(self) -> K:
        key = cast(
            K, f"{self._key_prefix}{len(self._counter) + self._key_index_offset}"
        )
        self._counter.update([key])
        return key

    def delete(self, key: K):
        self._counter.subtract([key])

    def contains(self, key: K) -> bool:
        return self.__contains__(key)

    def count(self) -> int:
        return self.__len__()
