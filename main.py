"""
Author:
Nilusink
"""
from classes import *


def main() -> None:
    _p1 = Player(position=Vec2.from_cartesian(
        x=100,
        y=910
    ), controls=(
        "d",
        "a",
        "SPACE"
    ), shoots=True)

    _p2 = Player(position=Vec2.from_cartesian(
        x=1000,
        y=900
    ), controls=(
        "RIGHT",
        "LEFT",
        "UP"
    ))

    Player(position=Vec2.from_cartesian(
        x=1800,
        y=0
    ))

    _scope = Scope()

    while True:
        Game.update()
        pg.display.update()


if __name__ == "__main__":
    main()
