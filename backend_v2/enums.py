from __future__ import annotations

from backend_v2.eenum import ExtendableEnum

__all__ = ['Color', 'PlaceableCardType', 'CardType', 'MoonPhase', 'Area', 'AnyResource']


class _ColorEnumTree(ExtendableEnum):
    # Colors
    PURPLE: Color = 1
    GREEN: Color = 2
    RED: Color = 3
    BLUE: Color = 4
    YELLOW: Color = 5
    # Card types
    ARTIFACT: PlaceableCardType = 6
    EVENT: CardType = 7
    # Moon phases
    LAST_TURN: MoonPhase = 8
    # Locations
    DISCARD: Area = 9
    HAND: Area = 10
    SPARE: Area = 11  # Card not used in the current game
    # Resources
    POINTS: AnyResource = 12


class AnyResource(_ColorEnumTree):
    _eenum_include_members_ = [
        _ColorEnumTree.PURPLE,
        _ColorEnumTree.GREEN,
        _ColorEnumTree.RED,
        _ColorEnumTree.BLUE,
        _ColorEnumTree.YELLOW,
        _ColorEnumTree.POINTS,
    ]


class Area(_ColorEnumTree):
    _eenum_include_members_ = [
        _ColorEnumTree.PURPLE,
        _ColorEnumTree.GREEN,
        _ColorEnumTree.RED,
        _ColorEnumTree.BLUE,
        _ColorEnumTree.YELLOW,
        _ColorEnumTree.ARTIFACT,
        _ColorEnumTree.DISCARD,
        _ColorEnumTree.HAND,
        _ColorEnumTree.SPARE
    ]


class CardType(_ColorEnumTree):
    _eenum_include_members_ = [
        _ColorEnumTree.PURPLE,
        _ColorEnumTree.GREEN,
        _ColorEnumTree.RED,
        _ColorEnumTree.BLUE,
        _ColorEnumTree.YELLOW,
        _ColorEnumTree.ARTIFACT,
        _ColorEnumTree.EVENT
    ]


class PlaceableCardType(Area, CardType):
    _eenum_include_members_ = [
        _ColorEnumTree.PURPLE,
        _ColorEnumTree.GREEN,
        _ColorEnumTree.RED,
        _ColorEnumTree.BLUE,
        _ColorEnumTree.YELLOW,
        _ColorEnumTree.ARTIFACT,
    ]


class MoonPhase(_ColorEnumTree):
    _eenum_include_members_ = [
        _ColorEnumTree.PURPLE,
        _ColorEnumTree.GREEN,
        _ColorEnumTree.RED,
        _ColorEnumTree.BLUE,
        _ColorEnumTree.YELLOW,
        _ColorEnumTree.LAST_TURN,
    ]


class Color(AnyResource, PlaceableCardType, MoonPhase):
    _eenum_include_members_ = [
        _ColorEnumTree.PURPLE,
        _ColorEnumTree.GREEN,
        _ColorEnumTree.RED,
        _ColorEnumTree.BLUE,
        _ColorEnumTree.YELLOW,
    ]
