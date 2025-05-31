from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet, TYPE_CHECKING, Iterable

from .enums import Area, AnyResource, CardType, Color

if TYPE_CHECKING:
    from .game import GameBackend
    from .card import Card

__all__ = ['Location', 'ResourceFilter', 'CardTypeFilter']


@dataclass
class Location:
    player: int
    area: Area
    key: int

    def get(self, game: GameBackend) -> Card:
        return game.get_areas_for(self.player)[self.area][self.key]

    def clear(self, game: GameBackend) -> Card:
        return game.get_areas_for(self.player)[self.area].pop(self.key)

    def put(self, game: GameBackend, card: Card):
        dest_area = game.get_areas_for(self.player)[self.area]
        # I wish there was a Python function for these 3 lines (insert value
        #  and return previous value)
        prev = dest_area.get(self.key)
        dest_area[self.key] = card
        return prev


@dataclass(frozen=True)
class ResourceFilter:
    allowed_resources: frozenset[AnyResource]

    def __init__(self, allowed_resources: AbstractSet[AnyResource]):
        object.__setattr__(self, 'allowed_resources', frozenset(allowed_resources))

    def is_allowed(self, c: AnyResource):
        return c in self.allowed_resources

    @classmethod
    def any_color(cls):
        return cls({*Color.members()})

    @classmethod
    def not_yellow(cls):
        return cls({*Color.members()} - {Color.YELLOW})

    @classmethod
    def not_red(cls):
        return cls({*Color.members()} - {Color.RED})


@dataclass(frozen=True)
class CardTypeFilter:
    allowed_types: frozenset[CardType]

    def __init__(self, allowed_types: Iterable[CardType]):
        object.__setattr__(self, 'allowed_types', frozenset(allowed_types))

    def is_allowed(self, c: CardType):
        return c in self.allowed_types

    @classmethod
    def any_type(cls):
        return cls(CardType.members())
