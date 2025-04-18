from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields
from typing import Generic, TypeVar, AbstractSet


T = TypeVar('T')
lookup_member = object()


def _is_descriptor_or_func(a: object):
    # Functions also have the descriptor stuff
    return (hasattr(a, '__get__') or
            hasattr(a, '__set__') or
            hasattr(a, '__delete__'))


class ExtendableEnumMeta(type, Generic[T]):
    _name_to_inst_: dict[str, ExtendableEnum[T]]
    _value_to_inst_: dict[T, ExtendableEnum[T]]
    _instances_: set[ExtendableEnum[T]]  # Fast containment check

    def __init__(cls, name: str, bases: tuple[type, ...], ns: dict[str, ...], **kwargs):
        super().__init__(name, bases, ns, **kwargs)
        cls._name_to_inst_ = {}
        cls._value_to_inst_ = {}
        for k, v in ns.items():
            if k.startswith('_') and k.endswith('_'):
                continue
            if _is_descriptor_or_func(v):
                continue
            if (inst := cls._value_to_inst_.get(v)) is None:
                if isinstance(v, ExtendableEnum):
                    inst = v
                    v = v.value
                else:
                    inst = cls(k, v)
            cls._value_to_inst_[v] = cls._name_to_inst_[k] = inst
            setattr(cls, k, inst)
        cls._instances_ = set(cls._name_to_inst_.values())

    def __contains__(self, item):
        if isinstance(item, ExtendableEnum):
            return item in self._instances_
        return item in self._name_to_inst_ or item in self._value_to_inst_

    def __getitem__(self, item):
        if isinstance(item, ExtendableEnum):
            return item
        try:
            return self._name_to_inst_[item]
        except KeyError:
            return self._value_to_inst_[item]

    def __iter__(self):
        yield from self._instances_

    def _copy_attrs(cls):
        cls._name_to_inst_ = cls._name_to_inst_.copy()
        cls._value_to_inst_ = cls._value_to_inst_.copy()
        cls._instances_ = cls._instances_.copy()


class ExtendableEnum(Generic[T], metaclass=ExtendableEnumMeta[T]):
    name: str
    value: T

    _init_ran_: bool = False

    def __new__(cls, name: str, value: T = lookup_member):
        if value is lookup_member:
            return cls[name]
        return super().__new__(cls)

    def __init__(self, name: str, value: T = lookup_member):
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

    def __init_subclass__(cls, **kwargs):
        cls._copy_attrs()  # So additions to subclass don't affect base class


class Color(ExtendableEnum):
    PURPLE = 1
    GREEN = 2
    RED = 3
    BLUE = 4
    YELLOW = 5


class PlaceableCardType(Color):
    ARTIFACT = 6


class CardType(PlaceableCardType):
    EVENT = 7


class MoonPhase(Color):
    LAST_TURN = 8


class Area(PlaceableCardType):
    DISCARD = 9
    HAND = 10
    NONE = 11


class AnyResource(Color):
    POINTS = 12


@dataclass
class Location:
    area: Area
    idx: int | None
    player: int | None


# Card types: CardTemplate should have frozen immutable attributes 'printed on
#  the physical card' and Card should have those attributes as frozen
#  but should have other non-frozen attributes. This is mainly po
# This is partially possible but not fully because:
#  - It doesn't let non-frozen dataclasses inherit from frozen ones
#  - It only lets frozen dataclasses inherit non-frozen ones if there's min.
#    1 frozen dataclass in the base classes in 3.11-3.12.
# Therefore, we can create a base _CommonCard class (non-frozen)
#  and have the Card (non-frozen) class inherit from it. Then, also have the
#  CardTemplate (frozen) class inherit from _CommonCard and an empty frozen
#  dataclass. However, in 3.13, they changed it so that for a dataclass to be
#  non-frozen, ALL its base classes must be non-frozen so this doesn't work.
# Therefore, we need a different approach. The main point of `frozen` is hashing
#  support. When I actually think about hashing, the CardTemplate should have
#  the standard 'all fields equal' hashing but for Card, it should be based on
#  id() because you can have 2 identical cards but they should be different
#  keys in a dict.
@dataclass(unsafe_hash=True)
class CardTemplate:  # Frozen-by-convention
    card_type: CardType
    effect: ...
    cost: CardCost
    always_triggers: bool = False
    is_starting_card: bool = False


@dataclass(eq=False)
class Card(CardTemplate):
    location: Location = None
    markers: int = 0

    def __eq__(self, other):
        return object.__eq__(self, other)  # id()-bsed equality for consistency

    def equals(self, other):
        # Still have the field-based equality available, Java-style
        if type(self) is not type(other):
            # Don't use NotImplemented because Python is a STUPID and
            #  bool(NotImplemented) = TypeError. WTF Python?!!
            return False
        # Pycharm, once again doesn't understand dataclasses
        # noinspection PyTypeChecker
        return all(getattr(self, f.name) == getattr(other, f.name)
                   for f in fields(self))  # Not writing out all the fields

    def __hash__(self):
        return object.__hash__(self)  # id()-based hash


@dataclass
class CardCost:
    possibilities: dict[ColorFilter, int]

    def matches_exact(self, resources: Counter[Color]):
        """Returns the first ColorFilter it matched"""
        for color_filter, n in self.possibilities.items():
            total_have = sum(resources.values())
            if n != total_have:
                continue  # Need exact
            # Fancy way of getting set of colors w/ amount>0 (`+counter` keeps >0 only)
            colors_have = {*(+resources)}
            if all(map(color_filter.is_allowed, colors_have)):
                return color_filter
        return None


@dataclass(frozen=True)
class ColorFilter:
    allowed_colors: frozenset[Color]

    def __init__(self, allowed_colors: AbstractSet):
        object.__setattr__(self, 'allowed_colors', frozenset(allowed_colors))

    def is_allowed(self, c: Color):
        return c in self.allowed_colors


@dataclass
class Player:
    idx: int  # Which player we are
    # Me when the code gets too generic... - we have 'areas' for each player:
    #  the hand, regular placed cards (1 for each type), placed artifacts, etc.
    # In effect an 'area' is a generalised 1D ordered list of cards.
    # It is done this way for easy location support and so cards can be moved
    #  in a general way (this requires a general notion of 'location').
    areas: dict[Area, list[Card]]
    resources: Counter[AnyResource]  # points are also a resource...
    # Used only at the final evaluation:
    final_score: int | None = None


@dataclass
class Game:
    players: list[Player]
    moon_phases: list[set[MoonPhase]]
    frontend: ...
    round_num: int
    turn_num: int
