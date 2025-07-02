from __future__ import annotations

import abc
from collections import Counter
from typing import Sequence, Collection

from .card import CardTemplate, CardCost, CardEffect
from .card_effects import *
from .common import ResourceFilter
from .enums import MoonPhase, AnyResource, Color, PlaceableCardType, CardType, Area

__all__ = ['IRuleset', 'DefaultRuleset']


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

    @abc.abstractmethod
    def get_adjacencies(self) -> dict[PlaceableCardType, Collection[PlaceableCardType]]:
        ...

    @abc.abstractmethod
    def get_starting_resources(self) -> Counter[AnyResource]:
        ...


# noinspection PyMethodMayBeStatic
class DefaultRuleset(IRuleset):
    _decks_cached: list[list[CardTemplate]] = None

    def _starting_card_effect(self, color: Color):
        if color != Color.YELLOW:
            return GainResource(color, 1)
        return ConvertEffect(SpendResource(ResourceFilter.not_yellow(), 1),
                             GainResource(Color.YELLOW, 1))

    def get_starting_cards(self) -> list[CardTemplate]:
        return [CardTemplate(c, self._starting_card_effect(c), CardCost.free(),
                             is_starting_card=True)
                for c in Color.members()]

    def get_deck(self, round_idx: int) -> list[CardTemplate]:
        return self._get_decks()[round_idx]

    cards_per_player = 6

    def get_moon_pool(self) -> Sequence[MoonPhase]:
        return [*Color.members()] * 2

    def get_swap_dirn(self, round_idx: int) -> int:
        return [1, -1, 1][round_idx]

    def resources_per_point(self, r: AnyResource) -> int:
        return {
            AnyResource.PURPLE: 3, AnyResource.GREEN: 3,  AnyResource.RED: -1,
            AnyResource.BLUE: 3,  AnyResource.YELLOW: 1, AnyResource.POINTS: 1
        }[r]

    def get_adjacencies(self) -> dict[PlaceableCardType, Collection[PlaceableCardType]]:
        return {Color.PURPLE: {Color.GREEN},
                Color.GREEN: {Color.PURPLE, Color.RED},
                Color.RED: {Color.GREEN, Color.BLUE},
                Color.BLUE: {Color.RED, Color.YELLOW},
                Color.YELLOW: {Color.BLUE}}

    def get_starting_resources(self) -> Counter[AnyResource]:
        return Counter(Color.members())   # 1 of each regular color

    @classmethod
    def _get_decks(cls):
        if cls._decks_cached is None:
            cls._decks_cached = cls._make_decks_inner()
        return cls._decks_cached

    # noinspection PyPep8Naming, PyPep8
    @classmethod
    def _make_decks_inner(cls) -> list[list[CardTemplate]]:
        # TODO: redo this function - it was copied from the old code so is
        #  consequently a nuclear blast crater/absolute train wreck/bombshell.
        Card = CT = CardTemplate
        CCO = CardCost.color_or_any  # (card cost old, i.e. the old args)

        GainPoints = lambda n: GainResource(AnyResource.POINTS, n)
        HasMarkers = lambda: GreaterThanCond(NumMarkers(), ConstMeasure(0))
        HasMagicsOfType = lambda tp, num: GreaterEqCond(CardsOfType(tp), ConstMeasure(num))
        DiscardedMin = lambda n: GreaterEqCond(DiscardedCards(), ConstMeasure(n))
        HasResource = lambda reso, n: GreaterEqCond(ResourceCount(reso), ConstMeasure(n))
        ForEachCardSet = ForEachColorSet
        ExecuteAnyColorTwice = ExecChosenColorNTimes
        ExecuteCardEffect = ExecOwnPlacedCard
        ExecuteColorsNotBiggest = ExecColorsNotBiggest
        ForEachOfChosenColor = ForEachDynChosenColor
        ForEachMagic = ForEachPlacedMagic
        Execute3TimesAndDiscard = ExecChosenNTimesAndDiscard
        MoveCardAndRunColor = MoveChosenAndExecNewColor

        # -------- Only modified below this to fix the functions --------
        def gain1(color: Color, cost: CardCost | None = None):
            if cost is None:
                cost = CardCost.free()
            return CT(color, GainResource(color, 1), cost)

        def gain2(color: Color, cost: CardCost):
            return CT(color, GainResource(color, 2), cost)

        def p_gain2_c1(cond_color: Color, cost_color: Color):
            return CT(p,
                      ConditionalEffect(
                          HasMagicsOfType(cond_color, 1),
                          GainResource(p, 2)),
                      CCO(cost_color, 1, 3))

        def exp_ef(ef: CardEffect):
            return EffectGroup(
                AddMarker(),
                ForEachMarker(ef)
            )

        def only2x(ef: CardEffect):
            return Group(
                ef,
                AddMarker(),
                ConditionalEffect(HasMarkers(), DiscardThis(), AddMarker())
            )

        def conv_ef(src_color: ResourceFilter | Color, src_n: int,
                    dest_color: Color, dest_n: int,
                    effect: CardEffect = NullEffect()) -> CardEffect:
            if not isinstance(src_color, ResourceFilter):
                src_color = ResourceFilter({src_color})
            return ConvertEffect(SpendResource(src_color, src_n),
                                 GainResource(dest_color, dest_n), effect)

        def a_most_5pt(color: Area):
            return CT(
                a, ConditionalEffect(MostCardsOfType(color), GainPoints(5)), free)

        def gain_rp(color: Color, color_amount: int, point_amount: int):
            return Group(GainResource(color, color_amount), GainPoints(point_amount))

        def p_cards_gain(req_color: PlaceableCardType, req_n: int,
                         p_n: int, pt_n: int, cost: CardCost):
            return CT(p, ConditionalEffect(
                HasMagicsOfType(req_color, req_n),
                gain_rp(p, p_n, pt_n)
            ), cost)

        def p_cards_3pt(req_color: PlaceableCardType, req_n: int, cost: CardCost):
            return CT(p, ConditionalEffect(
                HasMagicsOfType(req_color, req_n),
                GainPoints(3)
            ), cost)

        def a_2per_card(color: Color, pts: int = 2, cost: CardCost | None = None):
            if cost is None:
                cost = CCO(color, 2, 4)
            return CT(a, ForEachCardOfType(GainPoints(pts), color), cost)

        p, g, r, b, y, a, s = CardType
        nr = ResourceFilter.not_red()
        ny = ResourceFilter.not_yellow()
        Cost = CCO
        Group = EffectGroup
        Cond = ConditionalEffect
        free = CardCost.free()

        # -------- Not modified below this --------
        # keeps these ordered in this way:
        # p, g, r, b, y, a, s
        return [
            [
                # purple
                gain1(p),
                gain2(p, CCO(g, 2, 3)),
                p_gain2_c1(g, g),
                p_gain2_c1(r, y),
                p_gain2_c1(b, g),
                p_gain2_c1(y, y),
                # green
                gain1(g),
                gain2(g, CCO(r, 2, 2)),
                Card(g, GainResource(g, 1), Cost(p, 1, 3), True),
                Card(g, GainResource(g, 1), Cost(r, 2, 2), True),
                Card(g, exp_ef(GainResource(g, 1)), Cost(r, 1, 1)),
                Card(g, GainResource(g, 3), Cost(r, 3, 3)),
                # red
                gain1(r),
                gain2(r, Cost(g, 1, 3)),
                Card(r, Group(GainResource(r, 1), GainPoints(1)), Cost(b, 2, 4)),
                Card(r, conv_ef(nr, 1, r, 1, GainPoints(1)), Cost(g, 1, 3)),
                Card(r, exp_ef(GainResource(r, 1)), Cost(b, 1, 3)),
                Card(r, GainResource(r, 3), Cost(g, 2, 4)),
                # blue
                gain1(b),
                gain2(b, Cost(y, 1, 3)),
                Card(b, only2x(GainResource(b, 2)), Cost(r, 2, 2)),
                Card(b, only2x(GainResource(b, 3)), Cost(y, 1, 3)),
                Card(b, only2x(Group(GainResource(b, 2), GainPoints(2))), Cost(y, 1, 3)),
                Card(b, ConditionalEffect(DiscardedMin(3), GainPoints(1)), free),
                # yellow
                Card(y, conv_ef(ny, 1, y, 1), free),
                Card(y, conv_ef(ny, 3, y, 2), Cost(b, 2, 3)),
                Card(y, conv_ef(p, 2, y, 2), Cost(b, 1, 3)),
                Card(y, conv_ef(p, 2, y, 2), Cost(p, 1, 3)),
                Card(y, conv_ef(r, 3, y, 2), Cost(b, 1, 3)),
                Card(y, conv_ef(b, 2, y, 2), Cost(p, 1, 3)),
                # artifacts
                a_most_5pt(p),
                a_most_5pt(g),
                a_most_5pt(r),
                a_most_5pt(b),
                a_most_5pt(y),
                a_most_5pt(a)
            ], [
                # purple
                Card(p, Group(GainResource(p, 3), GainPoints(1)), Cost(g, 3, 6)),
                p_cards_gain(g, 1, 2, 1, Cost(y, 1, 4)),
                p_cards_gain(b, 2, 2, 2, Cost(y, 2, 6)),
                p_cards_gain(b, 2, 2, 2, Cost(g, 1, 3)),
                p_cards_gain(g, 1, 2, 2, Cost(g, 2, 4)),
                # green
                Card(g, Cond(HasResource(g, 6), GainPoints(2)), Cost(p, 3, 5)),
                Card(g, GainPoints(1), Cost(p, 1, 3), True),
                Card(g, gain_rp(g, 1, 1), Cost(r, 4, 4), True),
                Card(g, gain_rp(g, 2, 1), Cost(p, 3, 5)),
                Card(g, exp_ef(gain_rp(g, 1, 1)), Cost(p, 4, 2)),
                # red
                Card(r, gain_rp(r, 2, 1), Cost(g, 2, 4)),
                Card(r, gain_rp(r, 3, 2), Cost(b, 4, 6)),
                Card(r, conv_ef(nr, 4, r, 4, ExecuteCardEffect(1)), Cost(g, 2, 4)),
                Card(r, conv_ef(nr, 3, r, 3, GainPoints(2)), Cost(b, 2, 4)),
                Card(r, exp_ef(gain_rp(r, 1, 1)), Cost(b, 4, 6)),
                # blue
                Card(b, gain_rp(b, 3, 1), Cost(r, 4, 4)),
                Card(b, only2x(GainPoints(2)), Cost(r, 2, 2)),
                Card(b, only2x(GainPoints(3)), Cost(y, 1, 4)),
                Card(b, only2x(gain_rp(b, 2, 2)), Cost(y, 1, 4)),
                Card(b, Cond(DiscardedMin(7), gain_rp(b, 2, 2)), Cost(r, 3, 3)),
                # yellow
                Card(y, conv_ef(ny, 4, y, 3), Cost(r, 5, 5)),
                Card(y, conv_ef(p, 3, y, 3), Cost(p, 2, 4)),
                Card(y, conv_ef(g, 3, y, 3), Cost(p, 2, 4)),
                Card(y, conv_ef(b, 3, y, 3), Cost(p, 2, 4)),
                Card(y, conv_ef(b, 3, y, 3), Cost(b, 2, 4)),
                # artifacts
                a_2per_card(p),
                a_2per_card(g),
                a_2per_card(r, 2, Cost(r, 4, 4)),
                a_2per_card(b, 3),
                a_2per_card(y),
                Card(a, ForEachCardSet(GainPoints(5)), Cost(y, 1, 3)),
                # spells
                Card(s, ChooseFromDiscardOf(1), Cost(g, 1, 3)),
                Card(s, ChooseFromDiscardOf(0), Cost(b, 2, 4)),
                Card(s, ChooseFromDiscardOf(-1), Cost(p, 1, 3)),
                Card(s, ExecuteAnyColorTwice(), Cost(r, 5, 5)),
                Card(s, ExecuteColorsNotBiggest(), Cost(y, 2, 6)),
            ], [
                # purple
                p_cards_3pt(p, 3, Cost(y, 2, 5)),
                p_cards_3pt(g, 2, Cost(y, 1, 4)),
                p_cards_3pt(r, 2, Cost(y, 1, 4)),
                p_cards_3pt(b, 1, Cost(g, 2, 4)),
                p_cards_3pt(y, 2, Cost(g, 2, 4)),
                # green
                Card(g, gain_rp(g, 2, 2), Cost(r, 4, 4)),
                Card(g, Cond(HasResource(g, 6), GainPoints(3)), Cost(r, 4, 4)),
                Card(g, GainPoints(2), Cost(p, 4, 6), True),
                Card(g, GainResource(g, 4), Cost(p, 4, 6), True),
                Card(g, exp_ef(gain_rp(g, 2, 2)), Cost(r, 4, 4)),
                # red
                Card(r, gain_rp(r, 3, 3), Cost(b, 4, 6)),
                Card(r, Cond(HasResource(r, 6), GainPoints(3)), Cost(b, 3, 6)),
                Card(r, conv_ef(nr, 2, r, 2, GainPoints(3)), Cost(g, 2, 5)),
                Card(r, conv_ef(nr, 2, r, 2, ExecuteCardEffect()), Cost(g, 3, 5)),
                Card(r, exp_ef(gain_rp(r, 2, 2)), Cost(g, 4, 7)),
                # blue
                Card(b, gain_rp(b, 2, 2), Cost(y, 1, 4)),
                Card(b, only2x(GainPoints(4)), Cost(y, 2, 6)),
                Card(b, only2x(gain_rp(b, 3, 3)), Cost(r, 6, 6)),
                Card(b, only2x(GainPoints(5)), Cost(r, 7, 7)),
                Card(b, Cond(DiscardedMin(7), GainPoints(3)), Cost(y, 2, 6)),
                # artifacts
                Card(a, GainPoints(4), Cost(r, 4, 4)),
                Card(a, GainPoints(8), Cost(p, 9, 13)),
                Card(a, ForEachEmptyColor(GainPoints(3)), Cost(g, 3, 5)),
                Card(a, ForEachOfChosenColor(GainPoints(2)), Cost(y, 2, 4)),
                Card(a, ForEachMagic(GainPoints(1)), Cost(y, 5, 10)),
                Card(a, ForEachDiscard(GainPoints(1)), Cost(b, 8, 12)),
                # spells
                Card(s, ChooseFromDiscardOf(0), Cost(r, 3, 3)),
                Card(s, ExecuteAnyColorTwice(), Cost(g, 4, 6)),
                Card(s, ExecuteColorsNotBiggest(), Cost(p, 3, 5)),
                Card(s, Execute3TimesAndDiscard(), Cost(b, 3, 5)),
                Card(s, MoveCardAndRunColor(), Cost(y, 2, 6)),
            ]
        ]
