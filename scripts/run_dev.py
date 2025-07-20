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


def main():
    # Websocket thread is non-daemonic and will realise that it needs to die
    backend_th = threading.Thread(
        target=run_backend, name='Arcanar Backend: Main Thread', daemon=True)
    frontend_th = threading.Thread(target=run_frontend, name='Arcanar Frontend Runner')
    backend_th.start()
    frontend_th.start()
    while backend_th.is_alive() and frontend_th.is_alive():
        time.sleep(0.01)


if __name__ == '__main__':
    main()
