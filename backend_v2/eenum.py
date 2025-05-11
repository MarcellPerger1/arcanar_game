"""eenum.py - A type-safe enum class that supports inheritance.

Conceptually it works this way:

- Say we want enum ``Color`` to have members (R, G, B) and we want enum
  ``ColorEx`` to have (R, G, B, C, M, Y). Here, all instances of ``Color`` are
  instances of ``ColorEx`` (but not the other way round!).
- Hence, the set of instances of ``Color`` < set of instances of ``ColorEx``
  and so ``Color`` is a subclass of ``ColorEx`` (as it has LESS members).
- In terms of type theory, this is because enums are a sum type (like unions),
  not a product type (like structs).

Therefore, we 'ignore' (instead of add) members in subclasses using the
syntax ``CYAN=EXCLUDE_MEMBER`` or ``_eenum_exclude_members_=(...)``.
We also need a 'root' class for each 'enum tree' to indicate which classes
are compatible with each other (because multiple inheritance is supported).

For more details, read the code.
"""

from __future__ import annotations

import functools
import operator
from dataclasses import dataclass
from typing import Generic, TypeVar, Iterable

__all__ = ['ExtendableEnumMeta', 'ExtendableEnum', 'EXCLUDE_MEMBER']


T = TypeVar('T')
LOOKUP_MEMBER = object()
EXCLUDE_MEMBER = object()


def _is_func_or_descriptor(a: object):
    # Functions also have the descriptor stuff
    return (hasattr(a, '__get__') or
            hasattr(a, '__set__') or
            hasattr(a, '__delete__'))


@dataclass
class EnumHierarchyData:
    name_to_inst: dict[str, ExtendableEnum[T]]
    value_to_inst: dict[T, ExtendableEnum[T]]
    all_instances: set[ExtendableEnum[T]]  # Fast containment check

    @classmethod
    def empty(cls):
        return cls({}, {}, set())

    def inst_from_value(self, value: T | ExtendableEnum[T] | object,
                        allow_name: bool = False) -> ExtendableEnum[T] | None:
        if value in self.all_instances:
            return value
        if (inst := self.value_to_inst[value]) is not None:
            return inst
        if allow_name and (inst := self.name_to_inst[value]) is not None:
            return inst
        return None

    def create_new_inst(
            self, cls: type[ExtendableEnum[T]] | ExtendableEnumMeta[T],
            name: str, value: T):
        inst = cls(name, value)
        self.register_new_inst(inst)
        return inst

    def register_new_inst(self, inst: ExtendableEnum[T]):
        if inst.name in self.name_to_inst:
            raise ValueError("Duplicate name in eenum")
        if inst.value in self.value_to_inst:
            raise ValueError("eenum value already registered")
        self.all_instances.add(inst)
        self.name_to_inst[inst.name] = inst
        self.value_to_inst[inst.value] = inst

    def __contains__(self, item):
        if isinstance(item, ExtendableEnum):
            return item in self.all_instances
        return item in self.name_to_inst or item in self.value_to_inst

    def __getitem__(self, item) -> ExtendableEnum[T]:
        if isinstance(item, ExtendableEnum):
            if item in self.all_instances:
                return item
            raise KeyError(item)
        try:
            return self.name_to_inst[item]
        except KeyError:
            return self.value_to_inst[item]

    def normalise_item(self, item: ExtendableEnum[T] | str | T) -> ExtendableEnum[T]:
        return self[item]  # See definition above for why this works


# Inverted class hierarchy: if Bar adds extra enum members to Foo,
#  Foo is a subclass of Bar as all instances of Foo are instances of Bar too.
class ExtendableEnumMeta(type, Generic[T]):
    _eenum_top_: type[ExtendableEnum[T]] | None = None
    _eenum_data_: EnumHierarchyData
    _eenum_members_: set[ExtendableEnum[T]] | None

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
        eenum_bases = [b for b in bases if (issubclass(b, ExtendableEnum)
                                            and b != ExtendableEnum)]
        if len(eenum_bases) == 0:
            cls._eenum_top_ = None
            cls._eenum_members_ = None
            cls._eenum_data_ = EnumHierarchyData.empty()
            cls._init_members_from_ns(ns, None, allow_exclude=False)
            return
        eenum_tops = {b._eenum_top_ for b in eenum_bases}
        if len(eenum_tops) > 1:
            raise TypeError("Two unrelated enum trees have a null intersection")
        (top,) = eenum_tops
        cls._eenum_top_ = top
        cls._eenum_data_ = top._eenum_data_
        concrete_bases = [b for b in eenum_bases if b != top]
        possible_members = functools.reduce(
            operator.and_, [b._eenum_members_ for b in concrete_bases]
        ) if concrete_bases else None
        cls._eenum_members_ = cls._init_members_from_ns(
            # Makes no sense to allow exclude in a root class (would
            #  only be excluding from the current class)
            ns, possible_members, allow_exclude=possible_members is not None)

    def _init_members_from_ns(cls, ns: dict[str, object],
                              possible_members: set[ExtendableEnum[T]] | None,
                              allow_exclude: bool):
        """Sets members on class and updates hierarchy. Returns set of member
        objects (doesn't set _eenum_members_ because this effectively adds
        some possible values to the hierarchy but doesn't actually dictate
        that this class uses them. This is needed because the top should
        be able to declare some values that some classes could use (but
        subclasses can declare new ones)"""
        # If it only inherits from the top (possible_members=None), it can
        #  add new values (top might not list all possible members). Otherwise,
        #  it must 'conform' to the concrete superclasses (i.e. have a subset
        #  of their members) so can't add new members.
        allow_extensions = possible_members is None
        members_by_name = cls._get_raw_members_dict(ns, allow_extensions)
        exclude_names = cls._get_exclude_names_from_ns(ns, allow_exclude)
        if possible_members is not None:
            members_by_name = members_by_name or {m.name: m for m in possible_members}
        if allow_exclude:
            # We exclude based on instances, not names so excluding the base
            #  value excludes all the aliases too
            exclude_inst = {
                members_by_name[name] for name in exclude_names
                if name in members_by_name}  # Don't exclude if not present
            members_by_name = {
                name: inst for name, inst in members_by_name.items()
                if inst not in exclude_inst
            }
        members = {*members_by_name.values()}
        if possible_members is not None:
            if not members.issubset(possible_members):
                raise TypeError("Disallowed value in eenum, expected values to"
                                " be a subset of the superclass values.")
        if not members:
            raise TypeError("eenum has no possible values.")
        for k, inst in members_by_name.items():
            setattr(cls, k, inst)  # Replace with instances
        return members

    def _get_exclude_names_from_ns(cls, ns: dict[str, object], allow_exclude: bool):
        if (excl := getattr(cls, '_eenum_exclude_members_', None)) is not None:
            if not allow_exclude and excl:
                raise TypeError("Cannot exclude value in its defining eenum class")
            cls._eenum_exclude_members_ = None  # Don't inherit this
            return {cls._eenum_data_.normalise_item(m).name for m in excl}
        exclude_names = set()
        # TODO: option to use an attribute for these which overrides everything
        for k, v in ns.items():
            if cls._is_special_name(k) or _is_func_or_descriptor(v):
                continue
            if v is EXCLUDE_MEMBER:
                if not allow_exclude:
                    raise TypeError("Cannot exclude value in its defining eenum class")
                exclude_names.add(k)
        return exclude_names

    def _get_raw_members_dict(cls, ns: dict[str, object], allow_extensions: bool):
        if (members := getattr(cls, '_eenum_members_', None)) is not None:
            cls._eenum_members_ = None  # Don't inherit this
            # Need special-case method due to new 'extension' members
            return cls._get_members_from_attr(members, allow_extensions)
        members_by_name = {}
        for k, v in ns.items():
            if cls._is_special_name(k) or _is_func_or_descriptor(v):
                continue
            if v is EXCLUDE_MEMBER:
                continue
            if (inst := cls._eenum_data_.inst_from_value(v)) is None:
                # New thing, not an alias (No existing value)
                if not allow_extensions:
                    raise TypeError(
                        f"Disallowed new value ({k}) in eenum, "
                        f"values must be subset of the superclass values")
                # TODO: What if it raises an error later in the
                #  instantiation? This value thing will stay! BAD!!!
                #  Fixing it it too convoluted so I will simply call it
                #  undefined behavior. Enums should only really be declared
                #  at the top level (where exceptions aren't usually
                #  caught/ignored), not arbitrarily at runtime (where the
                #  exceptions could be caught and ignored) so this is only
                #  a minor problem.
                inst = cls._eenum_data_.create_new_inst(cls, k, v)
            else:
                # noinspection PyProtectedMember
                inst._on_adopted_(cls)
            members_by_name[k] = inst
        return members_by_name

    def _get_members_from_attr(cls, members: Iterable[str | T | ExtendableEnum[T]],
                               allow_extensions: bool):
        members_by_name = {}
        for v in members:
            if (inst := cls._eenum_data_.inst_from_value(v, allow_name=True)) is None:
                # New thing, not an alias (No existing value)
                if not allow_extensions:
                    raise TypeError(
                        f"Disallowed new value ({v}) in eenum, "
                        f"values must be subset of the superclass values")
                if isinstance(v, ExtendableEnum):  # Using ExtendableEnum ctor. nerd.
                    k = v.name
                    v = v.value
                elif isinstance(v, str):
                    k = v
                else:
                    raise TypeError("_eenum_members_ new values must be str (or instances)")
                inst = cls._eenum_data_.create_new_inst(cls, k, v)
            else:
                # noinspection PyProtectedMember
                inst._on_adopted_(cls)
            members_by_name[inst.name] = inst
        return members_by_name

    def __contains__(cls, item):  # TODO this should be the equivalent of isinstance
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

    def __len__(cls):
        return len(cls._eenum_members_)


class ExtendableEnum(Generic[T], metaclass=ExtendableEnumMeta[T]):
    name: str
    value: T

    # 'Lowest-down' class containing this instance. This might not exist
    #  uniquely as there may be two disjoint bottom classes. Therefore, it
    #  tries to find a sensible 'more specific class' (currently the one
    #  with the least other members)
    _eenum_canonical_class_: ExtendableEnumMeta[T]
    _init_ran_: bool = False

    _eenum_special_: bool = True  # ClassVar

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
        # This will be instantiated from the class first defining it which we
        #  treat as canonical until there's a better candidate.
        self._eenum_canonical_class_ = type(self)

    def __repr__(self):
        # TODO: behavior is undefined if name is not always the same.
        return f'{self._eenum_canonical_class_.__name__}.{self.name}'

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        if not isinstance(other, ExtendableEnum):
            return NotImplemented
        # Should really be a single shared reference but we check this anyway
        # noinspection PyProtectedMember
        return self._eenum_top_ == other._eenum_top_ and self.value == other.value

    def __hash__(self):
        # Value because name could have aliases
        return hash((self._eenum_top_, self.value))

    def _on_adopted_(self, into: ExtendableEnumMeta[T]):
        if (self._eenum_canonical_class_ is None
                or len(into) < len(self._eenum_canonical_class_)):
            self._eenum_canonical_class_ = into
            # self.__class__ = into  # TODO: is this a good idea??
