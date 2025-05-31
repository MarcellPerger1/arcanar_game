from __future__ import annotations

import abc

from ..util import JsonT


class JsonConnection(abc.ABC):
    @abc.abstractmethod
    def send(self, obj: JsonT):
        ...

    @abc.abstractmethod
    def receive(self) -> JsonT:
        ...
