from __future__ import annotations

import collections
from typing import TypeVar, Generic, Any

__all__ = ['JsonT', 'FrozenDict']

KT = TypeVar('KT', covariant=True)
VT = TypeVar('VT', covariant=True)

JsonT = dict[str, Any] | list[Any] | tuple[Any, ...] | float | int | str | bool | None


class FrozenDict(collections.abc.Mapping[KT, VT], Generic[KT, VT]):
    _dict: dict

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_dict', dict(*args, **kwargs))

    def __setattr__(self, key, value):
        if key == '_dict':
            raise AttributeError("Cannot set _dict attribute of frozendict")
        super().__setattr__(self, key, value)

    def copy(self):
        return FrozenDict(self._dict.copy())

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    @classmethod
    def fromkeys(cls, *args, **kwargs):
        self = FrozenDict()
        object.__setattr__(self, '_dict', dict.fromkeys(*args, **kwargs))
        return self

    def get(self, *args, **kwargs):
        return self._dict.get(*args, **kwargs)

    def __len__(self) -> int:
        return len(self._dict)

    def __getitem__(self, key):
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FrozenDict):
            other = other._dict
        return self._dict.__eq__(other)

    def __reversed__(self):
        return self._dict.__reversed__()

    def __or__(self, other):
        return FrozenDict(self._dict | other)

    def __ror__(self, other):
        return FrozenDict(other | self._dict)

    def __hash__(self):
        return hash(frozenset(self.items()))
