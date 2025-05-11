from __future__ import annotations

from backend_v2.eenum import ExtendableEnum

__all__ = ['Color', 'PlaceableCardType', 'CardType', 'MoonPhase', 'Area', 'AnyResource']


class _ColorEnumTree(ExtendableEnum):
    # Colors
    PURPLE = 1
    GREEN = 2
    RED = 3
    BLUE = 4
    YELLOW = 5
    # Card types
    ARTIFACT = 6
    EVENT = 7
    # Moon phases
    LAST_TURN = 8
    # Locations
    DISCARD = 9
    HAND = 10
    SPARE = 11  # Card not used in the current game
    # Resources
    POINTS = 12


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
