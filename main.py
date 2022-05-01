"""
Author:
Nilusink
"""

from core.server_connecter import Connection
from core.game import *


def main() -> None:
    # server = Connection(
    #     (config.dyn.server_ip, 12345)
    # )
    main_player = Player(spawn_point=Vec2.from_cartesian(
        x=100,
        y=910
    ),
        controlled=True,
        controls=(
        "d",
        "a",
        "SPACE",
        "s"
    ),
        shoots=True,
        respawns=True,
        name=str(randint(1, 10000000))
    )
    # dummy = Player(
    #     spawn_point=Vec2.from_cartesian(
    #         x=1000,
    #         y=50
    #     ),
    #     respawns=True,
    #     controlled=False,
    # )

    Turret(
        position=Vec2.from_cartesian(
            x=1000,
            y=700
        ),
        weapon=Sniper
    )

    while True:
        Game.update()
        # server.send_update(main_player)
        pg.display.update()


if __name__ == "__main__":
    main()
