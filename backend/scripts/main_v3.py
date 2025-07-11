import threading

import setpath

if setpath.setpath():
    from main_v3_client import main as client_main
    from main_v3_server import main as server_main


def main():
    client_th = threading.Thread(
        target=client_main, name='main_v3 example client', daemon=True)
    server_th = threading.Thread(
        target=server_main, name='main_v3 example server', daemon=True)
    client_th.start()
    server_th.start()
    while client_th.is_alive() and server_th.is_alive():
        client_th.join(0.005)
        server_th.join(0.005)


if __name__ == '__main__':
    main()
