from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet, TYPE_CHECKING

from .enums import Area, AnyResource
from .game import Game

if TYPE_CHECKING:
    from .card import Card


@dataclass
class Location:
    player: int | None
    area: Area
    key: int

    def clear(self, game: Game) -> Card:
        return game.get_areas_for(self.player)[self.area].pop(self.key)

    def put(self, game: Game, card: Card):
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
