import json
import sys

from game.backend import GameBackend, DefaultRuleset
from game.api.jsonify import *

import pprint


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


GameBackend(4, JsonAdapter(JC()), DefaultRuleset())
