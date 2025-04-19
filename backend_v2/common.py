from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet

from backend_v2.enums import Area, Color


@dataclass
class Location:
    area: Area
    idx: int | None
    player: int | None


@dataclass(frozen=True)
class ColorFilter:
    allowed_colors: frozenset[Color]

    def __init__(self, allowed_colors: AbstractSet):
        object.__setattr__(self, 'allowed_colors', frozenset(allowed_colors))

    def is_allowed(self, c: Color):
        return c in self.allowed_colors
