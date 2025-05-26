from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .enums import *
from .player import Player
from .ruleset import IRuleset


@dataclass
class GameBackend:
    frontend: ...
    ruleset: IRuleset  # Defines starting cards, deck, passing order, etc.
    players: list[Player]
    moon_phases: list[set[MoonPhase]]
    round_num: int
    turn_num: int
    # Only used at end
    players_ranked: list[Player] | None = None

    def __init__(self, n_players: int, frontend: ..., ruleset: IRuleset,
                 seed: int | str = None):
        self.frontend = frontend
        self.ruleset = ruleset
        if seed is None:
            # TODO: maybe this could be urandom/SystemRandom instead?
            seed = time.time_ns()
        self.seed = str(seed)
        self.players = [Player.new(i, self) for i in range(n_players)]
        self.round_num = 0
        self.turn_num = 0

    def run_game(self):
        for self.round_num in range(3):
            self.do_round()
        self.count_points()

    def do_round(self):
        self.prepare_round()
        for self.turn_num in range(6):
            if self.turn_num != 0:
                self.rotate_cards()
            self.do_turn()

    def prepare_round(self):
        self.prepare_hands()
        self.prepare_moon_phases()

    def prepare_hands(self):
        # TODO: this could break if there's not enough cards for everyone.
        #  Do we handle that or is that the ruleset's responsibility?
        deck = self.ruleset.get_deck(self.round_num).copy()
        self.get_rng('game.deck.shuffle', self.round_num).shuffle(deck)
        for p in self.players:
            p.init_hand_from_deck(deck)

    def prepare_moon_phases(self):
        # TODO: customise which ones are fixed from ruleset
        #  but what if they want to add a new color? Am I gonna have to
        #  do the dynamic (extendable) enum stuff?!
        # TODO: also customise moons per turn?
        # TODO: also customise length
        variable_phases = list(self.ruleset.get_moon_pool())
        self.get_rng('game.moons.shuffle', self.round_num
                     ).shuffle(variable_phases)
        self.moon_phases = [{variable_phases.pop(), variable_phases.pop()}
                            for _ in range(5)] + [{MoonPhase.LAST_TURN}]

    def rotate_cards(self):
        by = self.ruleset.get_swap_dirn(self.round_num)
        hands_old = [p.hand for p in self.players]
        for i, p in enumerate(self.players):
            # (i+by)-th player gets from i-th player so i-th player get from (i-by)-th
            p.hand = p.posses_area_obj(hands_old[(i - by) % self.n_players])

    def do_turn(self):
        # TODO: hooks for UI to display state changes
        for p in self.players:
            p.do_turn()

    def count_points(self):
        for p in self.players:
            p.count_points()
        self.players_ranked = sorted(self.players, key=lambda pl: pl.final_score)

    # TODO: could there be a cleaner way of doing this?
    def does_color_run(self, color: Color, is_last: bool):
        return color in self.curr_moons or (
            is_last and MoonPhase.LAST_TURN in self.curr_moons)

    def get_rng(self, reason: str, *args: object):
        seed_str = f'{self.seed}+[{reason}@{args!s}]'
        return random.Random(seed_str)

    @property
    def curr_moons(self):
        return self.moon_phases[self.turn_num]

    @property
    def n_players(self):
        return len(self.players)

    def get_areas_for(self, player: int | Player):
        if isinstance(player, Player):
            return player.areas
        return self.players[player].areas
