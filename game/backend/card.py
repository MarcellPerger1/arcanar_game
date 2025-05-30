from __future__ import annotations

import abc
from collections import Counter
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Mapping

from .common import Location, ResourceFilter
from .enums import CardType, Area, PlaceableCardType, AnyResource
from .util import FrozenDict

if TYPE_CHECKING:
    from .backend import Player, GameBackend
    from .ifrontend import IFrontend


__all__ = ['CardTemplate', 'Card', 'CardCost', 'CardEffect', 'EffectExecInfo',
           'CANT_EXEC']


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
    effect: CardEffect
    cost: CardCost
    always_triggers: bool = False
    is_starting_card: bool = False

    def instantiate(self, to_location: Location = None, markers: int = 0):
        """Recommended usage: don't specify new_location as computing that may
        be annoying and it doesn't actually attach this to the game. Instead,
        call with no args, then use one of ``attach_to()`` or ``append_to()``.
        Note that this method returns the Card in a slightly inconsistent state
        (location set to None). This means that any movement methods that
        attempt to remove the card from a previous location fail
        (apart from ``move()`` which is built to handle this).
        Also note that ``player`` **MUST** be specified otherwise the
        card doesn't know which player to attach to."""
        return Card(
            self.card_type, self.effect, self.cost, self.always_triggers,
            self.is_starting_card, to_location, markers
        )


@dataclass(eq=False)
class Card(CardTemplate):
    location: Location = None
    markers: int = 0

    def execute(self, player: Player):
        # Player is the player to execute the effects for (other players can
        #  execute a player's card and get the effect for themselves in
        #  theory - although maybe not with the base cards)
        info = EffectExecInfo(self, player)
        self.effect.execute(info)

    def detach(self, game: GameBackend):
        """Detach ourself from `self.location`"""
        popped = self.location.clear(game)
        # If we're not at that location, something has gone very, very wrong.
        assert popped is self

    def attach(self, game: GameBackend):
        """Attach to `self.location` in the `GameBackend`"""
        prev = self.location.put(game, self)
        assert prev is None  # Hope we haven't overwritten anything,

    def attach_to(self, game: GameBackend, location: Location):
        self.location = location
        self.attach(game)

    def move(self, game: GameBackend, to: Location):
        # Check for the case where it didn't have a location before
        if self.location is not None:
            self.detach(game)
        self.attach_to(game, to)

    def append_to(self, game: GameBackend, area: Area, player: int | Player = None):
        if player is None:
            player = self.location.player
        if not isinstance(player, Player):
            player = game.players[player]
        self.move(game, Location(player.idx, area, player.area_next_key(area)))

    def discard(self, game: GameBackend, player: int | Player = None):
        self.append_to(game, Area.DISCARD, player)

    def is_placed(self):
        return PlaceableCardType.has_instance(self.location.area)

    def is_dyn_executable(self):
        return CardType.has_instance(self.location.area)

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


@dataclass(init=False, frozen=True)
class CardCost:
    possibilities: FrozenDict[ResourceFilter, int]

    def __init__(self, possibilities: Mapping[ResourceFilter, int]):
        object.__setattr__(self, 'possibilities', FrozenDict(possibilities))

    def matches_exact(self, resources: Counter[AnyResource]):
        """Returns the first ColorFilter it matched"""
        resources = +resources  # Remove negative/zero values
        for color_filter, n in self.possibilities.items():
            total_have = sum(resources.values())
            if n != total_have:
                continue  # Need exact
            if all(map(color_filter.is_allowed, resources.keys())):
                return color_filter
        return None

    @classmethod
    def free(cls):
        return cls({ResourceFilter.any_color(): 0})

    @classmethod
    def color_or_any(cls, color: AnyResource, color_cost: int, wild_cost: int):
        return cls({ResourceFilter({color}): color_cost,
                    ResourceFilter.any_color(): wild_cost})


@dataclass
class EffectExecInfo:
    card: Card
    player: Player

    @property
    def game(self):
        return self.player.game

    @property
    def frontend(self) -> IFrontend:
        return self.game.frontend

    @property
    def ruleset(self):
        return self.game.ruleset


class CardEffect(abc.ABC):
    """An interface representing an executable effect of a card. Must be
    hashable to enable hashing of CardTemplate objects. Therefore, it
    must also be immutable. A @dataclass(frozen=True) class is recommended"""

    @abc.abstractmethod
    def execute(self, info: EffectExecInfo) -> object | None:
        ...


CANT_EXEC = object()
