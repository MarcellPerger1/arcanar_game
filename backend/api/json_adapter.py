from __future__ import annotations

from collections import Counter
from typing import Literal, Collection, TypeVar

from .json_connection import JsonConnection
from .json_deserialise import JsonDeserialiser
from .json_serialise import JsonSerialiser
from ..core import (Game, Player, IFrontend, Card, Location, Area,
                    CardCost, AnyResource, EffectExecInfo, Color,
                    CardTypeFilter, ResourceFilter, PlaceableCardType,
                    AdjacenciesMappingT)
from ..util import JsonT

__all__ = ['JsonAdapter']


T = TypeVar('T')


# TODO: need to make JsonAdapter more robust so it informs server on error.
class JsonAdapter(IFrontend):
    game: Game

    def __init__(self, conn: JsonConnection):
        self.conn = conn
        self.serialiser = JsonSerialiser()
        self.deserialiser = JsonDeserialiser()
        self._next_thread_id = 1

    def register_game(self, game: Game):
        self.game = game
        self.conn.init()
        self.send({
            'request': 'init',
            'server_version': '0.1.3',
            'api_version': 1,
        }, thread=False, state=False)
        self.send({
            'request': 'state',
        }, thread=False, state=True)

    def register_result(self, winners: list[Player]):
        self.send({
            'request': 'result',  # Other info will be in `state`
            'winners': [p.idx for p in winners]
        }, thread=False)
        # Don't send state for shutdown (no state changes after result)
        self.send({'request': 'shutdown'}, thread=False, state=False)
        self.conn.close()

    # region main (non-init/non-end) API
    def get_action_type(self, player: Player) -> Literal['buy', 'execute']:
        # TODO: somehow handle multiple people/clients! - LATER,
        #  for now, pass-n-play only
        resp = self.request({'request': 'action_type', 'player': player.idx})
        # TODO: perhaps repeat if invalid/resend it ?
        ac_type = resp['action_type']
        assert ac_type in ('buy', 'execute')
        return ac_type

    def get_discard(self, player: Player) -> Card:
        # TODO: allow cancellation back to choosing action_type from here
        #  /when choosing how to pay.
        resp = self.request({'request': 'discard_for_exec', 'player': player.idx})
        # TODO: somehow detect logic error vs invalid response
        card = self.deser_card_ref(resp['discard_for_exec'])
        assert card in player.cards_of_type(Area.HAND)
        return card

    def get_card_buy(self, player: Player) -> Card:
        resp = self.request({'request': 'buy_card', 'player': player.idx})
        card = self.deser_card_ref(resp['buy_card'])
        assert card in player.cards_of_type(Area.HAND)
        return card

    def get_card_payment(self, player: Player, cost: CardCost) -> Counter[AnyResource]:
        resp = self.request({'request': 'card_payment', 'player': player.idx,
                             'cost': self.ser(cost)})
        return self.deser(resp['card_payment'], Counter[AnyResource])

    def choose_color_exec(self, info: EffectExecInfo, n_times: int) -> Color:
        resp = self.request({'request': 'color_exec', 'n_times': n_times}, info=info)
        return self.deser(resp['color_exec'], Color)

    def choose_excl_color(self, info: EffectExecInfo,
                          top_colors: Collection[Color]) -> Color:
        resp = self.request({'request': 'color_excl',
                             'of_colors': self.ser(top_colors)}, info=info)
        return self.deser(resp['color_excl'], Color)

    def get_foreach_color(self, info: EffectExecInfo) -> Color:
        resp = self.request({'request': 'color_foreach'}, info=info)
        return self.deser(resp['color_foreach'], Color)

    def choose_from_discard(self, info: EffectExecInfo, target: Player,
                            filters: CardTypeFilter) -> Card:
        resp = self.request({
            'request': 'card_from_discard',
            'target_player': target.idx,
            'filters': self.ser(filters),  # Will get cards themselves in state
        }, info=info)
        card = self.deser_card_ref(resp['card_from_discard'])
        assert card.location.area == Area.DISCARD and card.location.player == target
        assert card.card_type in filters
        return card

    def choose_card_exec(self, info: EffectExecInfo, n_times: int,
                         discard: bool = False) -> Card:
        resp = self.request({'request': 'card_exec', 'n_times': n_times,
                             'discard': discard}, info=info)
        card = self.deser_card_ref(resp['card_exec'])
        assert Color.has_instance(card.location.area)
        assert card.location.player == info.player
        return card

    def get_spend(self, info: EffectExecInfo, filters: ResourceFilter,
                  amount: int) -> None | Counter[AnyResource]:
        resp = self.request({'request': 'spend_resources', 'amount': amount,
                             'filters': self.ser(filters)}, info=info)
        if (result_ser := resp['spend_resources']) is None:
            return None
        # TODO: could have more checking here - it happens in the Game backend,
        #  and there should be a way of telling IFrontend that it was invalid
        return self.deser(result_ser, Counter[AnyResource])

    def choose_card_move(self, info: EffectExecInfo,
                         adjacencies: AdjacenciesMappingT) -> Card | None:
        resp = self.request({'request': 'card_move',
                             'paths': self.ser(adjacencies)}, info=info)
        if (card_ser := resp['card_move']) is None:
            return None
        card = self.deser_card_ref(card_ser)
        assert Color.has_instance(card.location.area)
        assert card.location.player == info.player
        return card

    def choose_move_where(self, info: EffectExecInfo, card_to_move: Card,
                          possibilities: Collection[PlaceableCardType]
                          ) -> PlaceableCardType | None:
        resp = self.request({
            'request': 'where_move_card',
            'card': self.ser(card_to_move.location),
            'possibilities': self.ser(possibilities)}, info=info)
        if (dest_ser := resp['where_move_card']) is None:
            return None
        dest = self.deser(dest_ser, PlaceableCardType)
        assert dest in possibilities
        return dest
    # endregion

    # region Custom serialisers
    def deser_card_ref(self, ref_json: JsonT) -> Card:
        return self.deser(ref_json, Location).get(self.game)

    # noinspection PyMethodMayBeStatic
    def ser_effect_info_ref(self, info: EffectExecInfo):
        """Serialise EffectExecInfo into an object with **references** to the player/card"""
        # TODO: tests for this `.ser()` as it caused a bug (while sending spend_resource)
        return {'player': info.player.idx, 'card': self.ser(info.card.location)}

    def serialise_state(self) -> JsonT:
        return self.ser(self.game)  # Game contains all the state
    # endregion

    # region ser/deser methods
    def ser(self, o: object) -> JsonT:
        return self.serialiser.ser(o)

    def deser(self, j: JsonT, expect_tp: type[T]) -> T:
        return self.deserialiser.deser(j, expect_tp)
    # endregion

    # region send/receive/request (incl thread logic)
    def send(self, obj: dict[str, JsonT], *, thread=True, state=True,
             info: EffectExecInfo = None):
        """If thread is True, it returns an opaque 'thread id' that can be
        used to query replies to this message."""
        extra = {}
        if info is not None:
            extra |= {'exec_info': self.ser_effect_info_ref(info)}
        if state:
            extra |= {'state': self.serialise_state()}
        if (tid := self.alloc_thread() if thread else None) is not None:
            extra |= {'thread': tid}
        self.conn.send(obj | extra)
        return tid

    def request(self, req: dict[str, JsonT], state=True, info: EffectExecInfo = None):
        th = self.send(req, state=state, info=info)
        return self.receive(th)

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
    # endregion
