from __future__ import annotations

from dataclasses import dataclass

from .enums import *
from .player import Player
from .ruleset import IRuleset


@dataclass
class Game:
    frontend: ...
    ruleset: IRuleset  # Defines starting cards, deck, passing order, etc.
    players: list[Player]
    moon_phases: list[set[MoonPhase]]
    round_num: int
    turn_num: int
    # Only used at end
    winners: list[Player] | None

    def __init__(self, n_players: int, frontend: ..., ruleset: IRuleset):
        self.frontend = frontend
        self.ruleset = ruleset
        self.players = [Player.new(i, self) for i in range(n_players)]
        self.round_num = 0
        # TODO: finish the Game logic

    @property
    def n_players(self):
        return len(self.players)

    def get_areas_for(self, player: int | Player):
        if isinstance(player, Player):
            return player.areas
        return self.players[player].areas
