import sys

from websockets.sync.client import connect


def main():
    with connect("ws://localhost:3141") as ws:
        while True:
            try:
                print(ws.recv(1.0))
            except TimeoutError:
                ws.send(input("Enter data >>> "))
    print('Connection closed')


if __name__ == '__main__':
    main()
