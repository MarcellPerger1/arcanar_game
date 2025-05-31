import json
import sys

from server.api.json_adapter import JsonAdapter
from server.api.json_connection import JsonConnection
from server.core import Game, DefaultRuleset
from server.util import JsonT


class JC(JsonConnection):
    def send(self, obj: JsonT):
        print('Sent request:')
        json.dump(obj, sys.stdout)
        print()
        json.dump(obj, sys.stdout, separators=(',', ':'))
        print()
        json.dump(obj, sys.stdout, indent=2)

    def receive(self) -> JsonT:
        return None


if __name__ == '__main__':
    Game(4, JsonAdapter(JC()), DefaultRuleset())
