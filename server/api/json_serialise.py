from __future__ import annotations

import abc
from dataclasses import is_dataclass, fields as d_fields

from typing import Callable, Any, cast, Mapping, TYPE_CHECKING

# noinspection PyProtectedMember
from ..core.enums import _ColorEnumTree
from ..util import JsonT, FrozenDict

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

__all__ = ['JsonSerialiser', 'JsonSerFuncT']


JsonSerFuncT = Callable[['JsonSerialiser', Any], JsonT]
# Need variable outside class so can refer to it during the definition of the
#  class (i.e. using the decorator on its methods)
_json_serialiser_dispatch = {}


class JsonSerialiser:
    dispatch: dict[type, JsonSerFuncT] = _json_serialiser_dispatch

    def __init__(self):
        # Copy to instance so inst.serialiser_func only affects the instance
        self.dispatch = self.dispatch.copy()

    def serialiser_func(self: JsonSerialiser | type, *tps: type):
        def decor(fn: JsonSerFuncT):
            target_dict.update(dict.fromkeys(tps, fn))  # {*tps : fn}
            return fn

        try:
            called_on_class = isinstance(self, JsonSerialiser)
        except NameError:  # JsonSerialiser is not defined, i.e. in this class's definition
            target_dict = _json_serialiser_dispatch
            tps += (self,)
            return decor
        if called_on_class:
            # Called on the class, not an instance, so `self` is None
            target_dict = cast('type[JsonSerialiser]', __class__).dispatch
            tps += (self,)
        else:
            target_dict = self.dispatch
        return decor

    def ser(self, o: object) -> JsonT:
        for tp in type(o).__mro__:
            if (fn := self.dispatch.get(tp)) is not None:
                return fn(self, o)
        return self.ser_default(o)

    def ser_default(self, o: object):
        if is_dataclass(o):
            return self.ser_dataclass(o)
        raise TypeError(f"Cannot serialise object: {o}")

    @serialiser_func(int, float, str, bool, type(None))
    def ser_builtin_atom(self, o: int | float | str | bool | None) -> JsonT:
        return o

    @serialiser_func(list, tuple, set, frozenset)
    def ser_collection(self, o: list | tuple) -> JsonT:
        return [self.ser(inner) for inner in o]  # Convert to list

    @serialiser_func(dict, FrozenDict)
    def ser_mapping(self, o: Mapping):
        if (res := self._try_ser_mapping_as_object(o)) is not None:
            return res
        return self._ser_mapping_as_array(o)

    def _try_ser_mapping_as_object(self, o: Mapping) -> dict[str, Any] | None:
        result = {}
        for k, v in o.items():
            k_ser = self.ser(k)
            if isinstance(k_ser, (int, float, str, bool, type(None))):
                k_str = str(k_ser)
            else:
                return None  # Can't easily stringify key, so do array-style
            result[k_str] = self.ser(v)
        return result

    def _ser_mapping_as_array(self, o: Mapping) -> list[tuple[JsonT, JsonT]]:
        return [(self.ser(k), self.ser(v)) for k, v in o.items()]

    @serialiser_func(_ColorEnumTree)
    def ser_any_color_enum(self, o: _ColorEnumTree):
        return o.value

    def ser_dataclass(self, o: DataclassInstance) -> JsonT:
        # Note: the order here is more on an 'aesthetic choice' - I prefer the
        #  type to be first in my JSON
        res = {}
        # By default, include type if it implements an abstract class
        #  (that means there's likely other implementations).
        if getattr(res, '_ser_polymorphic_', abc.ABC in type(o).__mro__):
            res |= {'__class__': type(o).__name__}
        # noinspection PyDataclass
        res |= {f.name: self.ser(getattr(o, f.name)) for f in d_fields(o)
                if (hasattr(o, f.name)
                    and f.name not in getattr(o, '_ser_exclude_', ()))}
        return res
