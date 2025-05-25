from __future__ import annotations

import abc

from backend_v2.card import CardTemplate


class IRuleset(abc.ABC):
    @abc.abstractmethod
    def get_starting_cards(self) -> list[CardTemplate]:  # TODO: what args to give this
        ...

    @abc.abstractmethod
    def get_deck(self, round_idx: int) -> list[CardTemplate]:
        ...
