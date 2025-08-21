import shutil
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Mapping, Callable, Iterable
from typing import Any

import setpath

if setpath.setpath():
    from backend.api.json_adapter import JsonAdapter
    from backend.api.wesocket_conn import WebsocketConn, ServerThreadDied
    from backend.core import Game, DefaultRuleset


class BackendThread(threading.Thread):
    def __init__(self, group: None = None,
                 target: Callable[..., object] | None = None, name: str = None,
                 args: Iterable[Any] = (),
                 kwargs: Mapping[str, Any] | None = None,
                 *, daemon: bool | None = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.should_restart = False

    def run(self):
        try:
            super().run()
        except ServerThreadDied:
            self.should_restart = True
            raise  # Still display message, could have bug in server thread
        self.should_restart = True  # Reached end of game, restart for further testing


def run_backend():
    g = Game(4, JsonAdapter(WebsocketConn()), DefaultRuleset(),
             '1748776970931817000')
    g.run_game()


def run_frontend():
    p = subprocess.Popen(
        [shutil.which('npm'), 'run', 'dev', '--prefix', 'frontend', '--', *sys.argv[1:]],
        stdin=sys.stdin.fileno(), stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno(),
        text=True
    )
    while threading.main_thread().is_alive() and p.poll() is None:
        time.sleep(0.001)
    if p.poll() is None:  # still alive
        p.send_signal(signal.CTRL_C_EVENT)
        time.sleep(0.01)
        p.terminate()


def start_backend_th():
    # Websocket thread is non-daemonic and will realise that it needs to die
    backend_th = BackendThread(
        target=run_backend, name='Arcanar Backend: Main Thread', daemon=True)
    backend_th.start()
    return backend_th


def start_frontend_th():
    frontend_th = threading.Thread(target=run_frontend, name='Arcanar Frontend Runner')
    frontend_th.start()
    return frontend_th


def main():
    backend_th = start_backend_th()
    frontend_th = start_frontend_th()
    while frontend_th.is_alive():
        if not backend_th.is_alive():  # Restart it (webpage reload needs same data again)
            time.sleep(0.02)  # Give websocket thread time to die
            if not backend_th.should_restart:
                return  # Exit, frontend will see that we're dead and will exit
            backend_th = start_backend_th()
        time.sleep(0.01)


if __name__ == '__main__':
    main()
