#! /usr/bin/python3.10
"""
Author:
Nilusink
"""
import time

from core.server_connecter import Connection
from traceback import format_exc
from core.game import *


def main() -> None:
    # server = Connection(
    #     (config.dyn.server_ip, 12345)
    # )
    # main_player = Player(spawn_point=Vec2.from_cartesian(
    #     x=100,
    #     y=100
    # ),
    #     controlled=True,
    #     controls=(
    #     "d",
    #     "a",
    #     "SPACE",
    #     "s"
    # ),
    #     shoots=True,
    #     respawns=True,
    #     name=str(randint(1, 10000000))
    # )
    # dummy = Player(
    #     spawn_point=Vec2.from_cartesian(
    #         x=1000,
    #         y=50
    #     ),
    #     respawns=True,
    #     controlled=False,
    # )
    #
    # Turret(
    #     position=Vec2.from_cartesian(
    #         x=1920/2,
    #         y=1080/2,
    #     ),
    #     weapon=Minigun,
    # )

    # Turret(
    #     position=Vec2.from_cartesian(
    #         x=200,
    #         y=950
    #     ),
    #     weapon=Minigun,
    # )

    Turret(
        position=Vec2.from_cartesian(
            x=50,
            y=950
        ),
        weapon=Minigun
    )

    Javelin(
        Vec2.from_cartesian(944-300, 20),
        Vec2.from_cartesian(x=0, y=1),
        pg.sprite.Sprite()
    )

    Rocket(
        Vec2.from_cartesian(50, 0),
        Vec2.from_cartesian(x=0, y=1),
        pg.sprite.Sprite()
    )
    Rocket(
        Vec2.from_cartesian(30, 0),
        Vec2.from_cartesian(x=0, y=1),
        pg.sprite.Sprite()
    )
    Rocket(
        Vec2.from_cartesian(70, 0),
        Vec2.from_cartesian(x=0, y=1),
        pg.sprite.Sprite()
    )

    Javelin(
        Vec2.from_cartesian(944, 0),
        Vec2.from_cartesian(x=0, y=1),
        pg.sprite.Sprite()
    )

    Javelin(
        Vec2.from_cartesian(1500, 900),
        Vec2.from_cartesian(x=1, y=-1),
        pg.sprite.Sprite()
    )

    Javelin(
        Vec2.from_cartesian(944+300, 20),
        Vec2.from_cartesian(x=0, y=1),
        pg.sprite.Sprite()
    )

    while True:
        Game.update()
        # server.send_update(main_player)
        pg.display.update()


if __name__ == "__main__":
    try:
        main()

    except Exception:
        print(format_exc())
        Game.end()
        raise

    finally:
        Game.end()
