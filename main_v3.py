from server.api.json_adapter import JsonAdapter
from server.api.wesocket_conn import WebsocketConn
from server.core import Game, DefaultRuleset


def main():
    g = Game(4, JsonAdapter(wc := WebsocketConn()), DefaultRuleset())
    g.run_game()
    wc.close()


if __name__ == '__main__':
    main()
