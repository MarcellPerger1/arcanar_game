from backend.api.json_adapter import JsonAdapter
from backend.api.wesocket_conn import WebsocketConn
from backend.core import Game, DefaultRuleset


def main():
    g = Game(4, JsonAdapter(WebsocketConn()), DefaultRuleset())
    g.run_game()


if __name__ == '__main__':
    main()
