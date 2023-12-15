"""Helper functions for operations on circular lists."""
from typing import Generator, Tuple, TypeVar, cast

T = TypeVar("T")


def tuples(list_: list[T], length: int) -> Generator[Tuple[T, ...], None, None]:
    """Returns a generator over tuples of given length in a circular list.

    E.g: tuples([1, 2, 3, 4, 5], 4) => (1, 2, 3, 4), (2, 3, 4, 5), (3, 4, 5, 1), ...
    """
    return (
        tuple(list_[(index + offset) % len(list_)] for offset in range(length))
        for index in range(len(list_))
    )


def pairs(list_: list[T]) -> Generator[Tuple[T, T], None, None]:
    """Returns a generator over item pairs in a circular list.

    E.g: pairs([1, 2, 3]) => (1, 2), (2, 3), (3, 1).
    """
    return cast(Generator[Tuple[T, T], None, None], tuples(list_, 2))


def triplets(list_: list[T]) -> Generator[Tuple[T, T, T], None, None]:
    """Returns a generator over item triplets in a circular list.

    E.g: pairs([1, 2, 3]) => (1, 2, 3), (2, 3, 1), (3, 1, 2).
    """
    return cast(Generator[Tuple[T, T, T], None, None], tuples(list_, 2))


def circulated_to(list_: list[T], index: int) -> list[T]:
    """Returns a copy of a list circulated so the item at 'index' is last.

    E.g: circulated_to([1,2,3,4], 1) => [3, 4, 1, 2].
    """
    return list_[(index + 1) % len(list_) :] + list_[: (index + 1) % len(list_)]


def circulated_to_item(list_: list[T], item: T) -> list[T]:
    """Returns a copy of a list circulated so 'item' is last.

    E.g: circulated_to([1, 2, 3, 4], 3) => [4, 1, 2, 3].
    """
    return circulated_to(list_, list_.index(item))


def circulated_to_pair(list_: list[T], pair: Tuple[T, T]) -> list[T]:
    """Returns a copy of a list circulated to 'pair' is last.

    E.g: circulated_to_pair([1, 2, 3, 4, 3, 2], (4, 3)) => [2, 1, 2, 3, 4, 3].
    """
    return circulated_to(list_, list(pairs(list_)).index(pair) + 1)


def split_at(list_: list[T], index: int) -> Tuple[list[T], list[T]]:
    """Returns the two slices of a list split at 'index'.

    E.g: split_at([1, 2, 3, 4], 2) => ([1, 2], [3, 4]).
    """
    return (list_[: index % len(list_)], list_[index % len(list_) :])


def split_at_item(list_: list[T], item: T) -> Tuple[list[T], list[T]]:
    """Returns the two slices of a list split at 'item'.

    E.g: split_at_item([1, 2, 3, 4], 3) => ([1, 2, 3], [4]).
    """
    return split_at(list_, list_.index(item) + 1)


def split_at_pair(list_: list[T], pair: Tuple[T, T]) -> Tuple[list[T], list[T]]:
    """Returns the two slices of a list split at 'pair'.

    E.g: split_at_pair([1, 2, 3, 4, 3, 2], (3, 4)) => ([1, 2, 3, 4], [3, 2]).
    """
    return split_at(list_, list(pairs(list_)).index(pair) + 2)


def next_item(list_: list[T], item: T) -> T:
    """Returns the item after 'item' in the passed list."""
    return list_[(list_.index(item) + 1) % len(list_)]


def previous_item(list_: list[T], item: T) -> T:
    """Returns the item before 'item' in the passed list."""
    return list_[(list_.index(item) - 1) % len(list_)]
