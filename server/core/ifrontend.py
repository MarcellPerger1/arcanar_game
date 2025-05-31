from __future__ import annotations

import abc
from typing import Collection, Mapping, Literal, Counter, TYPE_CHECKING

from .common import ResourceFilter, CardTypeFilter
from .enums import Color, PlaceableCardType, AnyResource

if TYPE_CHECKING:
    from .game import Game
    from .card import EffectExecInfo, Card, CardCost
    from .player import Player

__all__ = ['IFrontend']

_AdjMappingT = Mapping[PlaceableCardType, Collection[PlaceableCardType]]


class IFrontend(abc.ABC):
    @abc.abstractmethod
    def register_game(self, game: Game):
        ...

    @abc.abstractmethod
    def get_spend(self, info: EffectExecInfo, filters: ResourceFilter,
                  amount: int) -> None | Counter[AnyResource]:
        ...

    @abc.abstractmethod
    def get_foreach_color(self, info: EffectExecInfo) -> Color:
        ...

    @abc.abstractmethod
    def choose_from_discard(self, info: EffectExecInfo, target: Player,
                            filters: CardTypeFilter) -> Card:
        ...

    @abc.abstractmethod
    def choose_card_exec(self, info: EffectExecInfo, n_times: int,
                         discard: bool = False) -> Card:
        ...

    @abc.abstractmethod
    def choose_color_exec(self, info: EffectExecInfo, n_times: int) -> Color:
        ...

    @abc.abstractmethod
    def choose_excl_color(self, info: EffectExecInfo,
                          top_colors: Collection[Color]) -> Color:
        ...

    @abc.abstractmethod
    def choose_card_move(self, info: EffectExecInfo,
                         adjacencies: _AdjMappingT) -> Card | None:
        ...

    @abc.abstractmethod
    def choose_move_where(self, info: EffectExecInfo, card_to_move: Card,
                          possibilities: Collection[PlaceableCardType]
                          ) -> PlaceableCardType | None:
        ...

    @abc.abstractmethod
    def get_action_type(self, player: Player) -> Literal['buy', 'execute']:
        ...

    @abc.abstractmethod
    def get_card_buy(self, player: Player) -> Card:
        ...

    @abc.abstractmethod
    def get_discard(self, player: Player) -> Card:
        ...

    @abc.abstractmethod
    def get_card_payment(self, player: Player, cost: CardCost) -> Counter[AnyResource]:
        ...

    @abc.abstractmethod
    def register_result(self, winners: list[Player]):
        ...
