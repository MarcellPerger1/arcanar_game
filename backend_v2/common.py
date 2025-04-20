from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet

from backend_v2.enums import Area, Color, AnyResource


@dataclass
class Location:
    area: Area
    idx: int | None
    player: int | None


@dataclass(frozen=True)
class ResourceFilter:
    allowed_resources: frozenset[AnyResource]

    def __init__(self, allowed_resources: AbstractSet[AnyResource]):
        object.__setattr__(self, 'allowed_resources', frozenset(allowed_resources))

    def is_allowed(self, c: AnyResource):
        return c in self.allowed_resources
