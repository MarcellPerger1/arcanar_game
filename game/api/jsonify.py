from __future__ import annotations

import abc
from dataclasses import is_dataclass, fields as d_fields
from typing import Any, Literal, Counter, Callable, Mapping, cast, TYPE_CHECKING

from ..backend import (GameBackend, Player, IFrontend, Card, Location, Area,
                       CardCost, AnyResource, ResourceFilter)
from ..backend.enums import _ColorEnumTree
from ..backend.util import FrozenDict

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

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
        # TODO: use int id - easier backcompat (can change names in code
        #  easily) and comparisons based on .value so this makes sense.
        ...

    def serialise_state(self) -> JsonT:
        # TODO: Game dataclass **MUST** be fixed for the serialisation to work
        # TODO: also check the other dataclasses
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


# TODO: deserialise
class JsonSerialiser:
    dispatch: dict[type, Callable[[JsonSerialiser, Any], JsonT]] = {}
    
    def __init__(self):
        # Copy to instance so inst.serialiser_func only affects the instance
        self.dispatch = self.dispatch.copy()

    def serialiser_func(self: JsonSerialiser | type, *tps: type):
        def decor(fn: Callable[[JsonSerialiser, Any], JsonT]):
            target.dispatch |= dict.fromkeys(tps, fn)  # {*tps : fn}
            return fn

        if not isinstance(self, JsonSerialiser):
            # Called on the class, not an instance, so `self` is None
            target = cast(type[JsonSerialiser], __class__)
            tps += self
        else:
            target = self
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

    @serialiser_func(list, tuple, set)
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
        # noinspection PyDataclass
        return {f.name: self.ser(getattr(o, f.name)) for f in d_fields(o)
                if hasattr(o, f.name)}
