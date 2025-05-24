from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import OrderedDict

from .card import Card
from .enums import *


@dataclass
class Player:
    idx: int  # Which player we are
    game: Game
    # Me when the code gets too generic... - we have 'areas' for each player:
    #  the hand, regular placed cards (1 for each type), placed artifacts, etc.
    # In effect an 'area' is a generalised 1D ordered sequence of cards.
    # It is done this way for easy location support and so cards can be moved
    #  in a general way (this requires a general notion of 'location').
    # We use OrderedDict so we can easily remove items from the middle.
    #  Inserting cards in the middle would be nice for later extensibility but
    #  that would require a custom dict+linkedlist hybrid so this is good
    #  enough for now, it can be extended **LATER**. It also allow fast
    #  insertion at both the start and end. We use `int` keys as a sort of
    #  'index' that can have gaps (like a JS sparse array). We get the index
    #  by simply doing `last key + 1` which should result in no conflicts
    #  if it remains sorted in order of key (it should). We don't use and
    #  OrderedSet as we still want a simple `Location` object.
    areas: dict[Area, OrderedDict[int, Card]]
    resources: Counter[AnyResource]  # points are also a resource...
    # Used only at the final evaluation:
    final_score: int | None = None

    def cards_of_type(self, tp: Area, include_starting=True):
        return (self.areas[tp] if include_starting else
                [c for c in self.areas[tp].values() if not c.is_starting_card])

    def num_cards_of_type(self, tp: Area, include_starting=False):
        return len(self.cards_of_type(tp, include_starting))

    def area_next_key(self, area: Area):
        last_key = next(reversed(self.areas[area].keys()))
        return last_key + 1  # Last one is biggest so should be no conflicts


@dataclass
class Game:
    players: list[Player]
    moon_phases: list[set[MoonPhase]]
    general_areas: dict[Area, OrderedDict[int, Card]]  # Areas not associated with a player
    frontend: ...
    round_num: int
    turn_num: int

    def get_areas_for(self, player: int | None):
        if player is None:
            return self.general_areas
        return self.players[player].areas
