from __future__ import annotations

from backend_v2.util import ExtendableEnum

__all__ = ['Color', 'PlaceableCardType', 'CardType', 'MoonPhase', 'Area', 'AnyResource']


class Color(ExtendableEnum):
    PURPLE = 1
    GREEN = 2
    RED = 3
    BLUE = 4
    YELLOW = 5


class PlaceableCardType(Color):
    ARTIFACT = 6


class CardType(PlaceableCardType):
    EVENT = 7


class MoonPhase(Color):
    LAST_TURN = 8


class Area(PlaceableCardType):
    DISCARD = 9
    HAND = 10
    NONE = 11


class AnyResource(Color):
    POINTS = 12
