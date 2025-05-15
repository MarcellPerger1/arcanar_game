from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Self

from typing_extensions import TypeGuard

from .card import Card
from .enums import *


@dataclass
class Player:
    idx: int  # Which player we are
    game: Game
    # Me when the code gets too generic... - we have 'areas' for each player:
    #  the hand, regular placed cards (1 for each type), placed artifacts, etc.
    # In effect an 'area' is a generalised 1D ordered list of cards.
    # It is done this way for easy location support and so cards can be moved
    #  in a general way (this requires a general notion of 'location').
    areas: dict[Area, list[Card]]
    resources: Counter[AnyResource]  # points are also a resource...
    # Used only at the final evaluation:
    final_score: int | None = None

    def num_cards_of_type(self, tp: Area, include_starting=False):
        return len(self.areas[tp] if include_starting else
                   [c for c in self.areas[tp] if not c.is_starting_card])


@dataclass
class Game:
    players: list[Player]
    moon_phases: list[set[MoonPhase]]
    frontend: ...
    round_num: int
    turn_num: int
