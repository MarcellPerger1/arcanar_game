from __future__ import annotations

from dataclasses import dataclass
from typing import OrderedDict

from .card import Card
from .enums import *
from .player import Player


@dataclass
class Game:
    players: list[Player]
    moon_phases: list[set[MoonPhase]]
    general_areas: dict[Area, OrderedDict[int, Card]]  # Areas not associated with a player
    frontend: ...
    round_num: int
    turn_num: int

    @property
    def n_players(self):
        return len(self.players)

    def get_areas_for(self, player: int | None):
        if player is None:
            return self.general_areas
        return self.players[player].areas
