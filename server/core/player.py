from __future__ import annotations

from collections import Counter, OrderedDict
from dataclasses import dataclass, replace as d_replace
from typing import Callable, TYPE_CHECKING, Sequence, MutableSequence

from .card import Card, CardTemplate, CardCost
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

    _ser_exclude_ = ('game',)

    @classmethod
    def new(cls, idx: int, game: Game):
        return cls(idx, game, {a: OrderedDict() for a in Area.members()}, Counter())

    def init_cards(self):  # Should only be called straight after, or in, new()
        for c_template in self.ruleset.get_starting_cards():
            c = c_template.instantiate()
            self.place_card(c)

    def place_card(self, card: Card):
        card_type = card.card_type
        assert PlaceableCardType.has_instance(card_type)
        return card.append_to(self.game, card_type, self)

    @property
    def frontend(self):
        return self.game.frontend

    @property
    def ruleset(self):
        return self.game.ruleset

    @property
    def discard(self):
        return self.areas[Area.DISCARD]

    @property
    def hand(self):
        return self.areas[Area.HAND]

    @hand.setter
    def hand(self, value: OrderedDict[int, Card]):
        self.areas[Area.HAND] = value

    def init_hand_from_deck(self, deck: MutableSequence[CardTemplate]):
        self.init_hand([deck.pop() for _ in range(self.ruleset.cards_per_player)])

    def init_hand(self, cards: Sequence[CardTemplate], discard_remaining=False):
        self.set_hand([c.instantiate() for c in cards], discard_remaining)

    def set_hand(self, cards: Sequence[Card], discard_remaining=False):
        # Clear any remaining cards
        while (pair := next(iter(self.hand.items()), None)) is not None:
            pair: tuple[int, Card]
            _, rem = pair
            if discard_remaining:
                rem.discard(self.game, self)
            else:
                rem.detach(self.game)
        for c in cards:
            # Must specify player (card has never seen us before)
            c.append_to(self.game, Area.HAND, self)

    def do_turn(self):
        cards_before = len(self.hand)
        action = self.frontend.get_action_type(self)
        if action == 'buy':
            self.action_place()
        elif action == 'execute':
            self.action_execute()
        else:
            raise AssertionError("Bad action from frontend")
        assert len(self.hand) == cards_before - 1

    def action_place(self):
        card = self.frontend.get_card_buy(self)
        self.pay_for_card(card.cost)
        if card.card_type == CardType.EVENT:
            card.execute(self)
            card.discard(self.game, self)
        else:
            self.place_card(card)

    def pay_for_card(self, cost: CardCost):
        payment = self.frontend.get_card_payment(self, cost)
        assert cost.matches_exact(payment)
        self.resources -= payment

    def action_execute(self):
        self.frontend.get_discard(self).discard(self.game, self)
        self.run_curr_magics()

    def run_curr_magics(self):
        self.execute_filtered(self.can_run_card)  # Cool!

    def can_run_card(self, card: Card):
        effective_color = card.location.area
        if not Color.has_instance(effective_color):
            return False
        is_last = self.cards_of_type(effective_color)[-1] is card
        return self.game.does_color_run(effective_color, is_last)

    def execute_filtered(self, predicate: Callable[[Card], bool]):
        for c in Color:
            for a in self.cards_of_type(c):
                if predicate(a):
                    a.execute(self)

    def count_points(self):
        for a in self.areas[Area.ARTIFACT].values():
            a.execute(self)
        self.final_score = sum([v // self.ruleset.resources_per_point(r)
                                for r, v in self.resources.items()])

    def posses_area_obj(self, area: OrderedDict[int, Card]):
        """Change the locations of cards in ``area`` to this player. This
        doesn't actually move the cards so **use with caution**!"""
        for c in area.values():
            c.location = d_replace(c.location, player=self.idx)
        return area

    def cards_of_type(self, tp: Area, include_starting=True):
        return (list(self.areas[tp].values()) if include_starting else
                [c for c in self.areas[tp].values() if not c.is_starting_card])

    def num_cards_of_type(self, tp: Area, include_starting=False):
        return len(self.cards_of_type(tp, include_starting))

    def area_next_key(self, area: Area):
        if len(self.areas[area]) == 0:
            return 0  # Default to 0 as the first key.
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
