from __future__ import annotations

import abc
from typing import Sequence

from .card import CardTemplate
from .enums import MoonPhase, AnyResource


class IRuleset(abc.ABC):
    @abc.abstractmethod
    def get_starting_cards(self) -> list[CardTemplate]:  # TODO: what args to give this
        ...

    @abc.abstractmethod
    def get_deck(self, round_idx: int) -> list[CardTemplate]:
        ...

    @property
    @abc.abstractmethod
    def cards_per_player(self) -> int:
        ...

    @abc.abstractmethod
    def get_moon_pool(self) -> Sequence[MoonPhase]:
        ...

    @abc.abstractmethod
    def get_swap_dirn(self, round_idx: int) -> int:
        ...

    @abc.abstractmethod
    def resources_per_point(self, r: AnyResource) -> int:
        ...
