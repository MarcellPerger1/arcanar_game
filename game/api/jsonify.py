from __future__ import annotations

import abc
from typing import Any, Literal, Counter

from ..backend import (GameBackend, Player, IFrontend, Card, Location, Area, CardCost,
                       AnyResource, ResourceFilter)

JsonT = dict[str, Any] | list[Any] | tuple[Any, ...] | float | int | str | bool | None


class JsonConnection(abc.ABC):
    @abc.abstractmethod
    def send(self, obj: JsonT):
        ...

    @abc.abstractmethod
    def receive(self) -> JsonT:
        ...


class JsonAdapter(IFrontend):
    game: GameBackend

    def __init__(self, conn: JsonConnection):
        self.conn = conn
        self._next_thread_id = 1

    def register_game(self, game: GameBackend):
        self.game = game
        self.send({
            'request': 'init',
            'server_version': '0.0.1',
            'api_version': 0,  # 1 will be when the API is at least semi-stable
        }, thread=False)

    def get_action_type(self, player: Player) -> Literal['buy', 'execute']:
        # TODO: somehow handle multiple people/clients! - LATER,
        #  for now, pass-n-play only
        th = self.send({'request': 'action_type', 'player': player.idx})
        resp = self.receive(th)
        # TODO: perhaps repeat if invalid/resend it ?
        ac_type = resp['action_type']
        assert ac_type in ('buy', 'execute')
        return ac_type

    def get_discard(self, player: Player) -> Card:
        # TODO: allow cancellation back to choosing action_type from here
        #  /when choosing how to pay.
        th = self.send({'request': 'discard_for_exec', 'player': player.idx})
        resp = self.receive(th)
        # TODO: somehow detect logic error vs invalid response
        card = self.deserialise_card_loc(resp['discard_for_exec'])
        assert card in player.cards_of_type(Area.HAND)
        return card

    def get_card_buy(self, player: Player) -> Card:
        th = self.send({'request': 'buy_card', 'player': player.idx})
        resp = self.receive(th)
        card = self.deserialise_card_loc(resp['buy_card'])
        assert card in player.cards_of_type(Area.HAND)
        return card

    def get_card_payment(self, player: Player, cost: CardCost) -> Counter[AnyResource]:
        th = self.send({'request': 'card_payment', 'player': player,
                        'cost': self.ser_cost(cost)})
        resp = self.receive(th)
        # TODO: how to deser Counter[AnyResource]? - can't have int keys,
        #  must have string. Put int-in-string or use names?
        ...

    def deserialise_card_loc(self, card: JsonT) -> Card:
        # TODO: we should have a general json serde that handles dataclasses
        #  etc. so we don't have to this for all objects
        loc = Location(
            card['player'],
            Area(card['area']),  # TODO: send int or name?
            card['key']
        )
        return loc.get(self.game)

    def ser_cost(self, cost: CardCost) -> JsonT:
        ...

    def ser_resource_filter(self, rf: ResourceFilter) -> JsonT:
        # TODO: how to serialise the enums - int id or name?
        ...

    def serialise_state(self) -> JsonT:
        ...  # TODO

    def send(self, obj: dict[str, JsonT], thread=True, state=True):
        """If thread is True, it returns an opaque 'thread id' that can be
        used to query replies to this message."""
        extra = {}
        if state:
            extra |= {'state': self.serialise_state()}
        if (tid := self.alloc_thread() if thread else None) is not None:
            extra |= {'thread': tid}
        self.conn.send(obj | extra)
        return tid

    def receive(self, th: int | None):  # No default so tid isn't accidentally forgotten
        if th is None:
            return self.conn.receive()
        received_th: int = -1  # Can't have this tid, start loop
        resp = None
        while received_th != th:
            # Discard everything else (those referred to older threads,
            #  can't refer to threads not created yet)
            resp = self.conn.receive()
            received_th = resp.pop('thread', -1)
        return resp

    def alloc_thread(self):
        th = self._next_thread_id
        self._next_thread_id += 1
        return th

    # TODO: these methods need to be implemented:
    #  - get_spend
    #  - get_foreach_color
    #  - choose_from_discard
    #  - choose_card_exec
    #  - choose_color_exec_twice
    #  - choose_excl_color
    #  - choose_card_move
    #  - choose_move_where
    #  - get_card_payment
