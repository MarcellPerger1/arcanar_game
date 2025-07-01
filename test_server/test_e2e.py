import json
import os
import sys
import threading
import time
import unittest
from pathlib import Path

from websockets import ConnectionClosedOK
from websockets.sync.client import connect, ClientConnection

from backend.api.json_adapter import JsonAdapter
from backend.api.wesocket_conn import WebsocketConn
from backend.core import Game, DefaultRuleset


_PORT = 5926


class E2ETestCase(unittest.TestCase):
    maxDiff = 65535

    _idx: int = -1
    _server_failed = False

    def setUp(self):
        orig_wd = os.getcwd()
        dirname = Path(__file__).parent
        os.chdir(dirname.parent)
        self.addCleanup(os.chdir, orig_wd)

    def start_server(self):
        self._server_th = threading.Thread(
            target=self.server_main, name='main_v3 example server', daemon=True)
        self._server_th.start()

    def server_main(self):
        try:
            g = Game(4, JsonAdapter(WebsocketConn(_PORT)),
                     DefaultRuleset(), seed='1748776970931817000')
            g.run_game()
        except Exception as e:
            self._server_failed = e
            raise

    # noinspection PyMethodMayBeStatic
    def _load_actions(self):
        with open('./test_server/test_e2e_data.json') as f:
            raw: list[dict[str, ...]] = json.load(f)
        return [next(iter(o.items())) for o in raw]

    def test(self):
        self.start_server()
        with connect(f"ws://localhost:{_PORT}") as ws:
            for self._idx, (tp, data) in enumerate(self._load_actions()):
                if self._server_failed:
                    self.fail("Server encountered error! See above for details.")
                if tp == 'send':
                    self.send_and_assert_no_recv(ws, data)
                elif tp == 'recv':
                    self.assert_recv(ws, data)
                elif tp == 'closed':
                    self.assert_conn_closed(ws)
                else:
                    assert 0
            # Wait for server to potentially raise any errors from our last response
            time.sleep(0.1)
            if self._server_failed:
                self.fail("Server encountered error! See above for details.")

    def send_and_assert_no_recv(self, ws: ClientConnection, data):
        # Test that server hasn't sent anything
        with self.assertRaises(TimeoutError, msg="Server shouldn't have sent anything"):
            actual = ws.recv(0.01)  # Raises TimeoutError if nothing to receive
            print(f'[LOC] In message number {self._idx}:')
            print(f'While trying to send {json.dumps(data)}:', file=sys.stderr)
            print(f'Server unexpectedly sent {actual}', file=sys.stderr)
        ws.send(json.dumps(data))

    def assert_recv(self, ws: ClientConnection, expected):
        try:
            actual_str = ws.recv(0.2)
        except TimeoutError:
            if self._server_failed:  # Could've failed trying to give us the response
                self.fail("Server encountered error! See above for details.")
            print('Please disregard the "connection handler failed" from the '
                  'server - it is a consequence of this test failing',
                  file=sys.stderr)
            self.fail("Expected message from server, didn't get any in 200ms."
                      " Perhaps it was expecting a message from us.")
        actual = json.loads(actual_str)
        if expected == actual:
            return
        print(f'[LOC] In message number {self._idx}', file=sys.stderr)
        print(f'Raw one-line jsons:', file=sys.stderr)
        print(f'  Expected: {json.dumps(expected, sort_keys=True)}', file=sys.stderr)
        print(f'  Actual  : {json.dumps(actual, sort_keys=True)}', file=sys.stderr)
        expected_raw = json.dumps(expected, sort_keys=True)
        actual_raw = json.dumps(actual, sort_keys=True)
        with self.subTest('Raw one-line jsons:'):
            self.assertEqual(expected_raw, actual_raw)
        expected_str = json.dumps(expected, sort_keys=True, indent=2)
        actual_str = json.dumps(actual, sort_keys=True, indent=2)
        with self.subTest('Multi-line jsons:'):
            self.assertEqual(expected_str, actual_str)
        with self.subTest('Objects:'):
            self.assertEqual(expected, actual)
        self.assertEqual(expected, actual)

    def assert_conn_closed(self, ws: ClientConnection):
        with self.assertRaises(ConnectionClosedOK, msg="Server should close connection"):
            ws.send('{}')  # Empty, should be ignored if server not closed (no thread=...)
            print(f'[LOC] In message number {self._idx}', file=sys.stderr)
