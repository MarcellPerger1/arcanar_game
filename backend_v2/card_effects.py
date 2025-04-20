from __future__ import annotations

import abc
from collections import Counter
from dataclasses import dataclass

from .card import CardEffect, EffectExecInfo, CannotExecute
from .common import ResourceFilter
from .enums import *


@dataclass(frozen=True)
class NullEffect(CardEffect):
    def execute(self, info: EffectExecInfo):
        pass


@dataclass(frozen=True)
class GainResource(CardEffect):
    resource: AnyResource
    amount: int

    def execute(self, info: EffectExecInfo):
        info.player.resources[self.resource] += self.amount


@dataclass(frozen=True)
class SpendResource(CardEffect):
    colors: ResourceFilter
    amount: int

    def execute(self, info: EffectExecInfo):
        # Let frontend handle the unambiguous case itself
        spent: Counter[AnyResource] = info.frontend.get_spend(self.colors, self.amount, info)
        if spent is None:
            raise CannotExecute()
        assert spent <= info.player.resources
        assert spent.total() == self.amount
        assert all(map(self.colors.is_allowed, +spent))  # are all positive colors allowed?
        info.player.resources -= spent


@dataclass(frozen=True, init=False)
class EffectGroup(CardEffect):
    """Will stop and fail itself if any of the sub-effects fail"""

    effects: tuple[CardEffect, ...]

    def __init__(self, *effects: CardEffect):
        object.__setattr__(self, 'effects', effects)

    def execute(self, info: EffectExecInfo):
        for e in self.effects:
            e.execute(info)


@dataclass(frozen=True, init=False)
class ConvertEffect(EffectGroup):
    """Gives the player the option to spend a resource(negative action) to
    get a positive effect and possibly a side effect. Allow the card execution
    to continue even if 'spend' action can't be met."""

    def __init__(self, spend: CardEffect, gain: CardEffect, effect: CardEffect = None):
        if effect is None:
            effect = NullEffect()
        super().__init__(spend, gain, effect)

    @property
    def spend(self):
        return self.effects[0]

    @property
    def gain(self):
        return self.effects[1]

    @property
    def effect(self):
        return self.effects[2]

    def execute(self, info: EffectExecInfo):
        try:
            self.spend.execute(info)
        except CannotExecute:
            return  # Allow separate parts to still run
        self.gain.execute(info)
        self.effect.execute(info)


@dataclass(frozen=True)
class AddMarker(CardEffect):
    amount: int = 1

    def execute(self, info: EffectExecInfo):
        info.card.markers += 1


@dataclass(frozen=True)
class _EffectManyTimes(CardEffect, abc.ABC):
    effect: CardEffect

    @abc.abstractmethod
    def get_times(self, info: EffectExecInfo) -> int:
        ...

    def execute(self, info: EffectExecInfo):
        for _ in range(self.get_times(info)):
            self.effect.execute(info)


@dataclass(frozen=True)
class ForEachMarker(_EffectManyTimes):
    def get_times(self, info: EffectExecInfo) -> int:
        return info.card.markers


@dataclass(frozen=True)
class ForEachCardOfType(_EffectManyTimes):
    def get_times(self, info: EffectExecInfo) -> int:
        return ...

