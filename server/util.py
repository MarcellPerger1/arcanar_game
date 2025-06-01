from __future__ import annotations

from typing import Any, TypeAlias, overload, Literal, TypeVar

from .frozendict import FrozenDict  # re-export

from _typeshed import SupportsDunderGT, SupportsDunderLT

__all__ = ['JsonT', 'FrozenDict', 'cmp']


T = TypeVar('T')


JsonT: TypeAlias = (dict[str, Any] | list[Any] | tuple[Any, ...]
                    | float | int | str | bool | None)


@overload
def cmp(a: T, b: SupportsDunderGT[T]) -> Literal[-1, 0, 1]: ...
@overload
def cmp(a: SupportsDunderLT[T], b: T) -> Literal[-1, 0, 1]: ...


def cmp(a, b):
    if a == b:
        return 0
    if a < b:
        return -1
    return +1
