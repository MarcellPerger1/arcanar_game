from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import OrderedDict, Callable, TYPE_CHECKING

from .card import Card
from .enums import *

if TYPE_CHECKING:
    from .game import Game


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

    @classmethod
    def new(cls, idx: int, game: Game, init_cards=True):
        self = cls(idx, game, {a: OrderedDict() for a in Area.members()}, Counter())
        if init_cards:
            self.init_cards()
        return self

    def init_cards(self):  # Should only be called straight after, or in, new()
        for c_template in self.ruleset.get_starting_cards():
            c = c_template.instantiate()
            self.place_card(c)

    def place_card(self, card: Card):
        card_type = card.card_type
        assert PlaceableCardType.has_instance(card_type)
        return card.append_to(self.game, card_type)

    @property
    def frontend(self):
        return self.game.frontend

    @property
    def ruleset(self):
        return self.game.ruleset

    @property
    def discard(self):
        return self.areas[Area.DISCARD]

    def cards_of_type(self, tp: Area, include_starting=True):
        return (self.areas[tp] if include_starting else
                [c for c in self.areas[tp].values() if not c.is_starting_card])

    def num_cards_of_type(self, tp: Area, include_starting=False):
        return len(self.cards_of_type(tp, include_starting))

    def area_next_key(self, area: Area):
        last_key = next(reversed(self.areas[area].keys()))
        return last_key + 1  # Last one is biggest so should be no conflicts

    # player_offset can be negative (i.e. previous player)
    def nth_next_player(self, player_offset: int):
        new_idx = (self.idx + player_offset) % self.game.n_players
        return self.game.players[new_idx]

    def exec_color(self, tp: Area, cond: Callable[[Card], bool] = None):
        for c in self.cards_of_type(tp):
            if cond is None or cond(c):
                c.execute(self)

    def exec_color_evergreens(self, tp: Area):
        self.exec_color(tp, lambda c: c.always_triggers)
