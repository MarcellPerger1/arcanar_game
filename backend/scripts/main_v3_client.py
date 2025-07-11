import setpath

if setpath.setpath():
    from websockets import ConnectionClosedOK
    from websockets.sync.client import connect


def main():
    with connect("ws://localhost:3141") as ws:
        try:
            while True:
                try:  # A little basic, if no data in 1s, assume we need to send
                    print(ws.recv(1.0))
                except TimeoutError:
                    ws.send(input("[client] Enter data >>> "))
        except ConnectionClosedOK:
            print('[client] Connection closed (OK)')


if __name__ == '__main__':
    main()
