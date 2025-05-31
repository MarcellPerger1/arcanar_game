from __future__ import annotations

import abc
import json
import queue
import threading
import time
from dataclasses import dataclass

from websockets.sync.server import serve, ServerConnection

from .json_connection import JsonConnection
from ..util import JsonT


class CloseConn(BaseException):
    pass


class _Instruction(abc.ABC):
    @abc.abstractmethod
    def run(self, conn: ServerConnection):
        ...


@dataclass
class _SendInstruction(_Instruction):
    data: str

    def run(self, conn: ServerConnection):
        conn.send(self.data)


@dataclass
class _ReceiveInstruction(_Instruction):
    def run(self, conn: ServerConnection):
        return conn.recv()


@dataclass
class _CloseInstruction(_Instruction):
    def run(self, conn: ServerConnection):
        raise CloseConn()


# TODO: need to make the JsonAdapter more robust so it calls close() on error too.
class WebsocketConn(JsonConnection):
    # noinspection PyAttributeOutsideInit
    def init(self):
        self._instruction_queue = queue.Queue[_Instruction]()
        self._results_queue = queue.Queue[str]()
        self._server_thread = threading.Thread(
            target=self._server_worker,
            name='WebSocket Server (Controller Thread)')

    def send(self, obj: JsonT):
        # Separators: no whitespace. Sort keys: so we don't give client any
        #  information about ordering in our sets (and therefore the hashing
        #  seed which could be used for DoS - although this is unlikely)
        data = json.dumps(obj, separators=(',', ':'), sort_keys=True)
        self._instruction_queue.put(_SendInstruction(data))

    def receive(self) -> JsonT:
        self._instruction_queue.put(_ReceiveInstruction())
        return json.loads(self._results_queue.get())

    def close(self):
        self._instruction_queue.put(_CloseInstruction())
        while self._server_thread.is_alive():
            time.sleep(0.001)

    def _server_worker(self):
        with serve(self._handler, 'localhost', 3141) as server:
            server.serve_forever()

    def _handler(self, conn: ServerConnection):
        try:
            while True:
                if not threading.main_thread().is_alive():
                    raise CloseConn()
                if (result := self._instruction_queue.get().run(conn)) is not None:
                    self._results_queue.put(result)
        except CloseConn:
            return
