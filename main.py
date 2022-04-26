"""
Author:
Nilusink
"""
from core.server_connecter import Connection
from core import *


TYPE: str = "server"   # can be "connect" or "server"


def main() -> None:
    server = Connection(
        ("127.0.0.1", 12345)
    )
    main_player = Player(spawn_point=Vec2.from_cartesian(
        x=100,
        y=910
    ), controls=(
        "d",
        "a",
        "SPACE"
    ), shoots=True,
        name="Niggl"
    )

    _scope = Scope()

    while True:
        Game.update()
        server.send_update(main_player)
        pg.display.update()


if __name__ == "__main__":
    main()
