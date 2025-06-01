import json
import os
import sys
import threading
import unittest
from pathlib import Path

from websockets import ConnectionClosedOK
from websockets.sync.client import connect, ClientConnection

from server.api.json_adapter import JsonAdapter
from server.api.wesocket_conn import WebsocketConn
from server.core import Game, DefaultRuleset


def server_main():
    g = Game(4, JsonAdapter(WebsocketConn()), DefaultRuleset(),
             seed='1748776970931817000')
    g.run_game()


class E2ETestCase(unittest.TestCase):
    maxDiff = 65535

    def setUp(self):
        orig_wd = os.getcwd()
        dirname = Path(__file__).parent
        os.chdir(dirname.parent)
        self.addCleanup(os.chdir, orig_wd)

    def start_server(self):
        # TODO: take port as args
        self._server_th = threading.Thread(
            target=server_main, name='main_v3 example server', daemon=True)
        self._server_th.start()

    # noinspection PyMethodMayBeStatic
    def _load_actions(self):
        with open('./test_server/test_e2e_data.json') as f:
            raw: list[dict[str, ...]] = json.load(f)
        return [next(iter(o.items())) for o in raw]

    def test(self):
        self.start_server()
        with connect("ws://localhost:3141") as ws:
            for tp, data in self._load_actions():
                if tp == 'send':
                    ws.send(json.dumps(data))
                elif tp == 'recv':
                    self.assert_recv(ws, data)
                elif tp == 'closed':
                    self.assert_conn_closed(ws)
                else:
                    assert 0

    def assert_recv(self, ws: ClientConnection, expected):
        actual_str = ws.recv()
        actual = json.loads(actual_str)
        if expected != actual:
            print('Raw one-line jsons:', file=sys.stderr)
            print(f'  Expected: {json.dumps(expected, sort_keys=True)}', file=sys.stderr)
            print(f'  Actual  : {json.dumps(actual, sort_keys=True)}', file=sys.stderr)
        self.assertEqual(expected, actual)

    def assert_conn_closed(self, ws: ClientConnection):
        with self.assertRaises(ConnectionClosedOK):
            ws.send('{}')  # Empty, should be ignored if server not closed (no thread=...)
