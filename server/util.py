from __future__ import annotations

from typing import Any, TypeAlias, overload, Literal, TypeVar, Callable, TYPE_CHECKING

from .frozendict import FrozenDict  # re-export

if TYPE_CHECKING:
    from _typeshed import SupportsDunderGT, SupportsDunderLT

__all__ = ['JsonT', 'FrozenDict', 'cmp']


T = TypeVar('T')
T_any_comp = TypeVar('T_any_comp', bound='SupportsDunderLT | SupportsDunderGT')


JsonT: TypeAlias = (dict[str, Any] | list[Any] | tuple[Any, ...]
                    | float | int | str | bool | None)


@overload
def cmp(a: T, b: SupportsDunderGT[T]) -> Literal[-1, 0, 1]: ...
@overload
def cmp(a: SupportsDunderLT[T], b: T) -> Literal[-1, 0, 1]: ...
@overload
def cmp(a: T, b: T, key: Callable[[T], T_any_comp]) -> Literal[-1, 0, 1]: ...


def cmp(a, b, key: Callable[[object], Any] = None):
    if key is not None:
        a = key(a)
        b = key(b)
    if a == b:
        return 0
    if a < b:
        return -1
    return +1
