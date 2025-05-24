from __future__ import annotations

from dataclasses import dataclass
from typing import OrderedDict

from .card import Card
from .enums import *
from .player import Player


@dataclass
class Game:
    frontend: ...
    rules: ...  # Defines starting cards, deck, passing order, etc.
    players: list[Player]
    moon_phases: list[set[MoonPhase]]
    general_areas: dict[Area, OrderedDict[int, Card]]  # Areas not associated with a player
    round_num: int
    turn_num: int
    # Only used at end
    winners: list[Player] | None

    def __init__(self, n_players: int, frontend: ..., rules: ...):
        self.players = [Player.new(i, self) for i in range(n_players)]
        self.general_areas = {a: OrderedDict() for a in Area.members()}
        self.frontend = frontend
        self.round_num = 0
        # TODO: finish the Game logic

    @property
    def n_players(self):
        return len(self.players)

    def get_areas_for(self, player: int | None):
        if player is None:
            return self.general_areas
        return self.players[player].areas
