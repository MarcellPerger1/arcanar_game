from __future__ import annotations

import functools
import operator
from dataclasses import dataclass
from typing import Generic, TypeVar, Iterable

__all__ = ['ExtendableEnumMeta2', 'ExtendableEnum2']


T = TypeVar('T')
LOOKUP_MEMBER = object()
EXCLUDE_MEMBER = object()


def _is_descriptor_or_func(a: object):
    # Functions also have the descriptor stuff
    return (hasattr(a, '__get__') or
            hasattr(a, '__set__') or
            hasattr(a, '__delete__'))


@dataclass
class EnumHierarchyData:
    name_to_inst: dict[str, ExtendableEnum2[T]]
    value_to_inst: dict[T, ExtendableEnum2[T]]
    all_instances: set[ExtendableEnum2[T]]  # Fast containment check

    def inst_from_value(self, value: T | ExtendableEnum2[T] | object
                        ) -> ExtendableEnum2[T] | None:
        if value in self.all_instances:
            return value
        if (inst := self.value_to_inst[value]) is not None:
            return inst
        return None

    def create_new_inst(
            self, cls: type[ExtendableEnum2[T]] | ExtendableEnumMeta2[T],
            name: str, value: T):
        inst = cls(name, value)
        self.register_new_inst(inst)
        return inst

    def register_new_inst(self, inst: ExtendableEnum2[T]):
        if inst.name in self.name_to_inst:
            raise ValueError("Duplicate name in eenum")
        if inst.value in self.value_to_inst:
            raise ValueError("eenum value already registered")
        self.all_instances.add(inst)
        self.name_to_inst[inst.name] = inst
        self.value_to_inst[inst.value] = inst

    def __contains__(self, item):
        if isinstance(item, ExtendableEnum2):
            return item in self.all_instances
        return item in self.name_to_inst or item in self.value_to_inst

    def __getitem__(self, item) -> ExtendableEnum2[T]:
        if isinstance(item, ExtendableEnum2):
            if item in self.all_instances:
                return item
            raise KeyError(item)
        try:
            return self.name_to_inst[item]
        except KeyError:
            return self.value_to_inst[item]


# Inverted class hierarchy: if Bar adds extra enum members to Foo,
#  Foo is a subclass of Bar as all instances of Foo are instances of Bar too.
class ExtendableEnumMeta2(type, Generic[T]):
    _eenum_top_: type[ExtendableEnum2[T]] | None = None
    _eenum_data_: EnumHierarchyData
    _eenum_members_: set[ExtendableEnum2[T]]

    @classmethod
    def _is_special_name(cls, name: str):
        return name.startswith('_') and name.endswith('_')  # sunder/dunder

    def __init__(cls, name: str, bases: tuple[type, ...], ns: dict[str, ...],
                 **kwargs):
        super().__init__(name, bases, ns, **kwargs)
        if ns.get('_eenum_special_'):  # Must be defined on the class itself, not inherited
            return
        else:
            cls._eenum_special_ = False  # Suppress inherited value
        # Ignore irrelevant non-enum mixins
        eenum_bases = [b for b in bases if issubclass(b, ExtendableEnum2)
                       and b != ExtendableEnum2]
        if len(eenum_bases) == 0:
            ...  # TODO init top!
        eenum_tops = {b._eenum_top_ for b in eenum_bases}
        if len(eenum_tops) > 1:
            raise TypeError("Two unrelated enum trees have a null intersection")
        (top,) = eenum_tops
        cls._eenum_top_ = top
        info = cls._eenum_data_ = top._eenum_data_
        # Bases without the `top` of the hierarchy
        concrete_bases = [b for b in eenum_bases if b != top]
        # If it only inherits from the top, it can add new values
        #  (top might not list all possible members). Otherwise, it must
        #  'conform' to the concrete superclasses (i.e. have a subset of
        #  their members)

        # TODO: branches v. similar, extract into one bit w/ callback like
        #  on_inst_error or maybe just a allow_new_inst kwarg
        if concrete_bases:
            # 'Simple' case (in theory) - no additions allowed
            possible_members = functools.reduce(
                operator.and_, [b._eenum_members_ for b in concrete_bases])
            # TODO: option to use an attribute for these which overrides everything
            ns_members_by_name = {}
            ns_exclude_names = set()
            for k, v in ns.items():
                if cls._is_special_name(k) or _is_descriptor_or_func(v):
                    continue
                if v is EXCLUDE_MEMBER:
                    ns_exclude_names.add(k)
                    continue
                if (inst := info.inst_from_value(v)) is None:
                    raise TypeError(  # New thing, not an alias, ERROR!
                        f"Disallowed new value ({k}) in eenum, "
                        f"values must be subset of the superclass values")
                ns_members_by_name[k] = inst
            members_by_name = ns_members_by_name or {m.name: m for m in possible_members}
            # We exclude based on instances, not names so excluding the base
            #  value excludes all the aliases too
            exclude_inst = {
                members_by_name[name] for name in ns_exclude_names
                if name in members_by_name}  # Don't exclude if not present
            members_by_name = {
                name: inst for name, inst in members_by_name.items()
                if inst not in exclude_inst
            }
            members = {*members_by_name.values()}
            if not members.issubset(possible_members):
                raise TypeError("Disallowed value in eenum, expected values to"
                                " be a subset of the superclass values.")
            if not members:
                raise TypeError("eenum has no possible values.")
        else:
            # We have no default set of members here so require the class
            #  to list all of them. There is also little need for
            #  EXCLUDE_MEMBER logic as we could just not define the member.
            # Therefore, for simplicity, we don't implement this here.
            members_by_name = {}
            for k, v in ns.items():
                if cls._is_special_name(k) or _is_descriptor_or_func(v):
                    continue
                if v is EXCLUDE_MEMBER:
                    raise TypeError("Cannot exclude value in its defining eenum class")
                # If we already have an instance, try to reuse it as much as possible
                if (inst := info.inst_from_value(v)) is None:
                    inst = info.create_new_inst(cls, k, v)  # Also updates _eenum_data_
                members_by_name[k] = inst
            members = {*members_by_name.values()}
            if not members:
                raise TypeError("eenum has no possible values.")
        cls._eenum_members_ = members

    def __contains__(cls, item):
        try:
            inst = cls._eenum_data_[item]
        except KeyError:
            return False
        return inst in cls._eenum_members_

    def __getitem__(cls, item):
        inst = cls._eenum_data_[item]
        if inst not in cls._eenum_members_:
            raise KeyError(item)
        return inst

    def __iter__(cls):
        yield from cls._eenum_members_


class ExtendableEnum2(Generic[T], metaclass=ExtendableEnumMeta2[T]):
    name: str
    value: T

    _init_ran_: bool = False
    _eenum_special_: bool = True

    def __new__(cls, name: str, value: T = LOOKUP_MEMBER):
        if value is LOOKUP_MEMBER:
            return cls[name]
        return super().__new__(cls)

    def __init__(self, name: str, value: T = LOOKUP_MEMBER):
        if self._init_ran_:
            return
        self._init_ran_ = True
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}.{self.name}'

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash((type(self), self.name))
