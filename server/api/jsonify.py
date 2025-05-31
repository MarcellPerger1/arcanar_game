from __future__ import annotations

import abc
import sys
import typing
from dataclasses import is_dataclass, fields as d_fields
from typing import (Any, Literal, Callable, Mapping, cast,
                    TYPE_CHECKING, Collection, Counter)

from .. import core as core_mod
from ..core import (Game, Player, IFrontend, Card, Location, Area,
                    CardCost, AnyResource, EffectExecInfo, Color, CardTypeFilter,
                    ResourceFilter, PlaceableCardType)
# noinspection PyProtectedMember
from ..core.enums import _ColorEnumTree
from ..core.ifrontend import _AdjMappingT
from ..util import FrozenDict, JsonT

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

T = typing.TypeVar('T')


class JsonConnection(abc.ABC):
    @abc.abstractmethod
    def send(self, obj: JsonT):
        ...

    @abc.abstractmethod
    def receive(self) -> JsonT:
        ...


class JsonAdapter(IFrontend):
    game: Game

    def __init__(self, conn: JsonConnection):
        self.conn = conn
        self.serialiser = JsonSerialiser()
        self.deserialiser = JsonDeserialiser()
        self._next_thread_id = 1

    def register_game(self, game: Game):
        self.game = game
        self.send({
            'request': 'init',
            'server_version': '0.1.0',
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
                         adjacencies: _AdjMappingT) -> Card | None:
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
        return {'player': info.player.idx, 'card': info.card.location}

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


# Need variable outside class so can refer to it during the definition of the
#  class (i.e. using the decorator on its methods)
_json_serialiser_dispatch = {}
_json_deserialiser_dispatch = {}
JsonSerFuncT = Callable[['JsonSerialiser', Any], JsonT]
JsonDeserFuncT = Callable[['JsonDeserialiser', JsonT, type], Any]


class JsonSerialiser:
    dispatch: dict[type, JsonSerFuncT] = _json_serialiser_dispatch
    
    def __init__(self):
        # Copy to instance so inst.serialiser_func only affects the instance
        self.dispatch = self.dispatch.copy()

    def serialiser_func(self: JsonSerialiser | type, *tps: type):
        def decor(fn: JsonSerFuncT):
            target_dict.update(dict.fromkeys(tps, fn))  # {*tps : fn}
            return fn

        try:
            called_on_class = isinstance(self, JsonSerialiser)
        except NameError:  # JsonSerialiser is not defined, i.e. in this class's definition
            target_dict = _json_serialiser_dispatch
            tps += (self,)
            return decor
        if called_on_class:
            # Called on the class, not an instance, so `self` is None
            target_dict = cast('type[JsonSerialiser]', __class__).dispatch
            tps += (self,)
        else:
            target_dict = self.dispatch
        return decor

    def ser(self, o: object) -> JsonT:
        for tp in type(o).__mro__:
            if (fn := self.dispatch.get(tp)) is not None:
                return fn(self, o)
        return self.ser_default(o)

    def ser_default(self, o: object):
        if is_dataclass(o):
            return self.ser_dataclass(o)
        raise TypeError(f"Cannot serialise object: {o}")

    @serialiser_func(int, float, str, bool, type(None))
    def ser_builtin_atom(self, o: int | float | str | bool | None) -> JsonT:
        return o

    @serialiser_func(list, tuple, set, frozenset)
    def ser_collection(self, o: list | tuple) -> JsonT:
        return [self.ser(inner) for inner in o]  # Convert to list

    @serialiser_func(dict, FrozenDict)
    def ser_mapping(self, o: Mapping):
        if (res := self._try_ser_mapping_as_object(o)) is not None:
            return res
        return self._ser_mapping_as_array(o)

    def _try_ser_mapping_as_object(self, o: Mapping) -> dict[str, Any] | None:
        result = {}
        for k, v in o.items():
            k_ser = self.ser(k)
            if isinstance(k_ser, (int, float, str, bool, type(None))):
                k_str = str(k_ser)
            else:
                return None  # Can't easily stringify key, so do array-style
            result[k_str] = self.ser(v)
        return result

    def _ser_mapping_as_array(self, o: Mapping) -> list[tuple[JsonT, JsonT]]:
        return [(self.ser(k), self.ser(v)) for k, v in o.items()]

    @serialiser_func(_ColorEnumTree)
    def ser_any_color_enum(self, o: _ColorEnumTree):
        return o.value

    def ser_dataclass(self, o: DataclassInstance) -> JsonT:
        # Note: the order here is more on an 'aesthetic choice' - I prefer the
        #  type to be first in my JSON
        res = {}
        # By default, include type if it implements an abstract class
        #  (that means there's likely other implementations).
        if getattr(res, '_ser_polymorphic_', abc.ABC in type(o).__mro__):
            res |= {'__class__': type(o).__name__}
        # noinspection PyDataclass
        res |= {f.name: self.ser(getattr(o, f.name)) for f in d_fields(o)
                if (hasattr(o, f.name)
                    and f.name not in getattr(o, '_ser_exclude_', ()))}
        return res


class JsonDeserialiser:
    dispatch: dict[type, JsonDeserFuncT] = {}

    def __init__(self):
        # Copy to instance so inst.serialiser_func only affects the instance
        self.dispatch = self.dispatch.copy()

    def deserialiser_func(self: JsonDeserialiser | type, *tps: type):
        def decor(fn: JsonDeserFuncT):
            target_dict.update(dict.fromkeys(tps, fn))  # {*tps : fn}
            return fn

        try:
            called_on_class = isinstance(self, JsonDeserialiser)
        except NameError:  # JsonDeserialiser not defined, i.e. in this class's definition
            target_dict = _json_deserialiser_dispatch
            tps += (self,)
            return decor
        if called_on_class:
            # Called on the class, not an instance, so `self` is None
            target_dict = cast('type[JsonDeserialiser]', __class__).dispatch
            tps += (self,)
        else:
            target_dict = self.dispatch
        return decor

    def deser(self, j: JsonT, tp: type[T]) -> T:
        # Interestingly, also works for generic instances, like list[int]
        for tp in tp.__mro__:
            if (fn := self.dispatch.get(tp)) is not None:
                return fn(self, j, type)
        return self.deser_default(j, tp)

    def deser_default(self, j: JsonT, tp: type):
        if is_dataclass(tp):
            return self.deser_dataclass(j, tp)
        raise TypeError(f"Cannot serialise into type {tp.__qualname__}")

    @deserialiser_func(int, float, str, bool, type(None))
    def ser_builtin_atom(self, j: JsonT, tp: type) -> Any:
        assert isinstance(j, tp)
        return j

    @deserialiser_func(list, tuple, set, frozenset)
    def deser_collection(self, j: JsonT, tp: type):
        (inner_tp,) = typing.get_args(tp)
        return tp([self.deser(v, inner_tp) for v in j])

    @deserialiser_func(dict, FrozenDict, Mapping)
    def deser_mapping(self, j: JsonT, tp: type):
        if isinstance(j, list):
            return self._deser_mapping_array(j, tp)
        assert isinstance(j, dict)
        return self._deser_mapping_object(j, tp)

    def _deser_mapping_array(self, j: list, tp: type):
        kt, vt = typing.get_args(tp)
        return tp({self.deser(k, kt): self.deser(v, vt) for k, v in j})

    def _deser_mapping_object(self, j: dict[str, Any], tp: type):
        kt, vt = typing.get_args(tp)
        return {self._deser_mapping_key(k, kt): self.deser(v, vt) for k, v in j.items()}

    # Need separate func, Counter only has one type arg so doesn't work with code above.
    @deserialiser_func(Counter)
    def deser_counter(self, j: JsonT, tp: type):
        # noinspection PyTypeHints
        return Counter(self.deser_mapping(j, dict[typing.get_args(tp)[0], int]))

    # noinspection PyMethodMayBeStatic
    def _deser_mapping_key(self, j: str, tp: type):
        if issubclass(tp, str):
            return j
        elif issubclass(tp, bool):
            return {'False': False, 'True': True}[j]
        elif tp is type(None):
            assert j == 'None'
            return j
        elif isinstance(tp, int):
            return int(j)
        elif isinstance(tp, float):
            return float(j)
        raise AssertionError("Bad key type for mapping-from-object")

    @deserialiser_func(_ColorEnumTree)
    def deser_any_color_enum(self, j: JsonT, tp: type):
        return tp(j)  # Use that class's ctor

    def deser_dataclass(self, j: JsonT, tp: type | type[DataclassInstance]):
        assert isinstance(j, dict)
        # TODO: maybe use constructor instead - although some of them are
        #  different to the default (e.g. Game) so maybe not?
        #  In any case, this must be though over a bit more.
        inst = tp.__new__(tp)
        for k, v in j.items():  # (k must already be a string as it's a JSON object key)
            v_new = self.deser(v, self._get_dcls_attr_type(tp, k))
            object.__setattr__(inst, k, v_new)
        return inst

    @classmethod
    def _get_dcls_attr_type(cls, dcls: type, name: str):
        annot = cls._get_dcls_attr_annot(dcls, name)
        if not isinstance(annot, str):
            return annot
        globalns = getattr(sys.modules.get(dcls.__module__), '__dict__', {})
        # Not |= so we don't overwrite the actual module's globals
        globalns = globalns | dict(vars(core_mod))
        localns = vars(dcls)
        return eval(annot, globalns, localns)

    @classmethod
    def _get_dcls_attr_annot(cls, dcls: type, name: str) -> str | type:
        # Pycharm most certainly doesn't understand dataclasses...
        # noinspection PyTypeChecker,PyDataclass
        field_or_empty = [f for f in d_fields(dcls) if f.name == name]
        if len(field_or_empty) != 0:
            return field_or_empty[0].type
        tp = dcls.__annotations__.get(name)
        if tp is None:
            raise TypeError(f"Cannot determine type for field {dcls.__name__}.{name}")
        return tp
