import shutil
import signal
import subprocess
import sys
import threading
import time

import setpath

if setpath.setpath():
    from backend.api.json_adapter import JsonAdapter
    from backend.api.wesocket_conn import WebsocketConn
    from backend.core import Game, DefaultRuleset


def run_backend():
    g = Game(4, JsonAdapter(WebsocketConn()), DefaultRuleset(),
             '1748776970931817000')
    g.run_game()


def run_frontend():
    p = subprocess.Popen(
        [shutil.which('npm'), 'run', 'dev', '--prefix', 'frontend'],
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
    backend_th = threading.Thread(
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
            backend_th = start_backend_th()
        time.sleep(0.01)


if __name__ == '__main__':
    main()
