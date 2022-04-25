"""
Author:
Nilusink
"""
import numpy as np


# constants
PI: float = 3.1415926535897932384626433832


class Vec2:
    x: float
    y: float
    angle: float
    length: float

    def __init__(self) -> None:
        self.__x: float = 0
        self.__y: float = 0
        self.__angle: float = 0
        self.__length: float = 0

    # variable getters / setters
    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, value: float) -> None:
        self.__x = value
        self.__update("c")

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value: float) -> None:
        self.__y = value
        self.__update("c")

    @property
    def angle(self) -> float:
        """
        value in radian
        """
        return self.__angle

    @angle.setter
    def angle(self, value: float) -> None:
        """
        value in radian
        """
        self.__angle = value
        self.__update("p")

    @property
    def length(self) -> float:
        return self.__length

    @length.setter
    def length(self, value: float) -> None:
        self.__length = value
        self.__update("p")

    # interaction
    def split_vector(self, direction: "Vec2") -> tuple["Vec2", "Vec2"]:
        """
        :param direction: A vector facing in the wanted direction
        :return: tuple[Vector in only that direction, everything else]
        """
        a = (direction.angle - self.angle)
        facing = Vec2.from_polar(angle=direction.angle, length=self.length * np.cos(a))
        other = Vec2.from_polar(angle=direction.angle - PI / 2, length=self.length * np.sin(a))

        return facing, other

    # maths
    def __add__(self, other) -> "Vec2":
        if type(other) == Vec2:
            return Vec2.from_cartesian(x=self.x + other.x, y=self.y + other.y)

        return Vec2.from_cartesian(x=self.x + other, y=self.y + other)

    def __sub__(self, other) -> "Vec2":
        if type(other) == Vec2:
            return Vec2.from_cartesian(x=self.x - other.x, y=self.y - other.y)

        return Vec2.from_cartesian(x=self.x - other, y=self.y - other)

    def __mul__(self, other) -> "Vec2":
        if type(other) == Vec2:
            return Vec2.from_polar(angle=self.angle + other.angle, length=self.length * other.length)

        return Vec2.from_cartesian(x=self.x * other, y=self.y * other)

    def __truediv__(self, other) -> "Vec2":
        return Vec2.from_cartesian(x=self.x / other, y=self.y / other)

    # internal functions
    def __update(self, calc_from: str) -> None:
        """
        :param calc_from: polar (p) | cartesian (c)
        """
        if calc_from in ("p", "polar"):
            self.__x = np.cos(self.angle) * self.length
            self.__y = np.sin(self.angle) * self.length

        elif calc_from in ("c", "cartesian"):
            self.__length = np.sqrt(self.x**2 + self.y**2)
            self.__angle = np.arctan2(self.y, self.x)

        else:
            raise ValueError("Invalid value for \"calc_from\"")

    def __abs__(self) -> float:
        return np.sqrt(self.x**2 + self.y**2)

    def __repr__(self) -> str:
        return f"<\n" \
               f"\tVec2:\n" \
               f"\tx:{self.x}\ty:{self.y}\n" \
               f"\tangle:{self.angle}\tlength:{self.length}\n" \
               f">"

    # static methods.
    # creation of new instances
    @staticmethod
    def from_cartesian(x: float, y: float) -> "Vec2":
        p = Vec2()
        p.x = x
        p.y = y

        return p

    @staticmethod
    def from_polar(angle: float, length: float) -> "Vec2":
        p = Vec2()
        while angle > 2*PI:
            angle -= 2*PI
        while angle < 0:
            angle += 2*PI
        p.angle = angle
        p.length = length

        return p
