from __future__ import annotations

import sys
import typing
from collections import Counter
from dataclasses import is_dataclass, fields as d_fields
from typing import Callable, Any, cast, Mapping, TYPE_CHECKING, TypeVar

from .. import core as core_mod
# noinspection PyProtectedMember
from ..core.enums import _ColorEnumTree
from ..util import JsonT, FrozenDict

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

__all__ = ['JsonDeserialiser', 'JsonDeserFuncT']


T = TypeVar('T')
JsonDeserFuncT = Callable[['JsonDeserialiser', JsonT, type], Any]

# Need variable outside class so can refer to it during the definition of the
#  class (i.e. using the decorator on its methods)
_json_deserialiser_dispatch = {}


class JsonDeserialiser:
    dispatch: dict[type, JsonDeserFuncT] = _json_deserialiser_dispatch

    def __init__(self):
        # Copy to instance so inst.serialiser_func only affects the instance
        self.dispatch = self.dispatch.copy()

    def deserialiser_func(self: JsonDeserialiser | type, *tps: type):
        def decor(fn: JsonDeserFuncT):
            target_dict.update(dict.fromkeys(tps, fn))  # {*tps : fn}
            return fn

        try:
            called_on_class = isinstance(self, JsonDeserialiser)
        except NameError:  # JsonDeserialiser not defined, i.e. in this class's definition
            target_dict = _json_deserialiser_dispatch
            tps += (self,)
            return decor
        if called_on_class:
            # Called on the class, not an instance, so `self` is None
            target_dict = cast('type[JsonDeserialiser]', __class__).dispatch
            tps += (self,)
        else:
            target_dict = self.dispatch
        return decor

    def deser(self, j: JsonT, tp: type[T]) -> T:
        cls: type = typing.get_origin(tp)  # type: ignore  # Pycharm is stupid, once again
        if cls is None:
            cls = tp  # Must be a regular class - those have origin as None
        for supercls in cls.__mro__:
            if (fn := self.dispatch.get(supercls)) is not None:
                return fn(self, j, tp)
        return self.deser_default(j, tp)

    def deser_default(self, j: JsonT, tp: type):
        if is_dataclass(tp):
            return self.deser_dataclass(j, tp)
        raise TypeError(f"Cannot serialise into type {tp.__qualname__}")

    @deserialiser_func(int, float, str, bool, type(None))
    def ser_builtin_atom(self, j: JsonT, tp: type) -> Any:
        assert isinstance(j, tp)
        return j

    @deserialiser_func(list, tuple, set, frozenset)
    def deser_collection(self, j: JsonT, tp: type):
        (inner_tp,) = typing.get_args(tp)
        return tp([self.deser(v, inner_tp) for v in j])

    @deserialiser_func(dict, FrozenDict, Mapping)
    def deser_mapping(self, j: JsonT, tp: type):
        if isinstance(j, list):
            return self._deser_mapping_array(j, tp)
        assert isinstance(j, dict)
        return self._deser_mapping_object(j, tp)

    def _deser_mapping_array(self, j: list, tp: type):
        kt, vt = typing.get_args(tp)
        return tp({self.deser(k, kt): self.deser(v, vt) for k, v in j})

    def _deser_mapping_object(self, j: dict[str, Any], tp: type):
        kt, vt = typing.get_args(tp)
        return {self._deser_mapping_key(k, kt): self.deser(v, vt) for k, v in j.items()}

    # Need separate func, Counter only has one type arg so doesn't work with code above.
    @deserialiser_func(Counter)
    def deser_counter(self, j: JsonT, tp: type):
        # noinspection PyTypeHints
        return Counter(self.deser_mapping(j, dict[typing.get_args(tp)[0], int]))

    # noinspection PyMethodMayBeStatic
    def _deser_mapping_key(self, j: str, tp: type):
        if issubclass(tp, str):
            return j
        elif issubclass(tp, bool):
            return {'False': False, 'True': True}[j]
        elif tp is type(None):
            assert j == 'None'
            return j
        elif isinstance(tp, int):
            return int(j)
        elif isinstance(tp, float):
            return float(j)
        raise AssertionError("Bad key type for mapping-from-object")

    @deserialiser_func(_ColorEnumTree)
    def deser_any_color_enum(self, j: JsonT, tp: type):
        return tp(j)  # Use that class's ctor

    def deser_dataclass(self, j: JsonT, tp: type | type[DataclassInstance]):
        assert isinstance(j, dict)
        # TODO: maybe use constructor instead - although some of them are
        #  different to the default (e.g. Game) so maybe not?
        #  In any case, this must be though over a bit more.
        inst = tp.__new__(tp)
        for k, v in j.items():  # (k must already be a string as it's a JSON object key)
            v_new = self.deser(v, self._get_dcls_attr_type(tp, k))
            object.__setattr__(inst, k, v_new)
        return inst

    @classmethod
    def _get_dcls_attr_type(cls, dcls: type, name: str):
        annot = cls._get_dcls_attr_annot(dcls, name)
        if not isinstance(annot, str):
            return annot
        globalns = getattr(sys.modules.get(dcls.__module__), '__dict__', {})
        # Not |= so we don't overwrite the actual module's globals
        globalns = globalns | dict(vars(core_mod))
        localns = vars(dcls)
        return eval(annot, globalns, localns)

    @classmethod
    def _get_dcls_attr_annot(cls, dcls: type, name: str) -> str | type:
        # Pycharm most certainly doesn't understand dataclasses...
        # noinspection PyTypeChecker,PyDataclass
        field_or_empty = [f for f in d_fields(dcls) if f.name == name]
        if len(field_or_empty) != 0:
            return field_or_empty[0].type
        tp = dcls.__annotations__.get(name)
        if tp is None:
            raise TypeError(f"Cannot determine type for field {dcls.__name__}.{name}")
        return tp
