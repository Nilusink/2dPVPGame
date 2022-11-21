"""
Author:
Nilusink
"""
import typing as tp
import numpy as np


# constants
PI: float = 3.1415926535897932384626433832


def calculate_shot(target_delta: "Vec2", bullet_speed: float) -> float:
    """
    calculate the shooting angle for a bullet to hit a target

    :param target_delta: difference between the shooter and the target
    :param bullet_speed: the bullets initial velocity
    :return: the angle shoot at
    """
    shot_length = target_delta.length
    x, y = target_delta.xy
    v = bullet_speed
    t = shot_length / v
    a = np.arcsin((9.81 * t**2 + 2 * y) / (2 * t * v))

    # for correct orientation
    tmp = Vec2.from_polar(a, 1)
    if target_delta.x < 0:
        tmp.x *= -1

    tmp.mirror(target_delta)
    return tmp.angle


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
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value
        self.__update("c")

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value
        self.__update("c")

    @property
    def xy(self):
        return self.__x, self.__y

    @xy.setter
    def xy(self, xy):
        self.__x = xy[0]
        self.__y = xy[1]
        self.__update("c")

    @property
    def angle(self):
        """
        value in radian
        """
        return self.__angle

    @angle.setter
    def angle(self, value):
        """
        value in radian
        """
        value = self.normalize_angle(value)

        self.__angle = value
        self.__update("p")

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value
        self.__update("p")

    @property
    def polar(self):
        return self.__angle, self.__length

    @polar.setter
    def polar(self, polar):
        self.__angle = polar[0]
        self.__length = polar[1]
        self.__update("p")

    # interaction
    def split_vector(self, direction):
        """
        :param direction: A vector facing in the wanted direction
        :return: tuple[Vector in only that direction, everything else]
        """
        a = (direction.angle - self.angle)
        facing = Vec2.from_polar(angle=direction.angle, length=self.length * np.cos(a))
        other = Vec2.from_polar(angle=direction.angle - PI / 2, length=self.length * np.sin(a))

        return facing, other

    def copy(self):
        return Vec2().from_cartesian(x=self.x, y=self.y)

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "length": self.length,
        }

    def normalize(self) -> "Vec2":
        self.length = 1
        return self

    def mirror(self, mirror_by: "Vec2") -> "Vec2":
        mirror_by = mirror_by.copy().normalize()
        ang_d = mirror_by.angle - self.angle
        self.angle = mirror_by.angle + 2 * ang_d
        return self

    # maths
    def __add__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x + other.x, y=self.y + other.y)

        return Vec2.from_cartesian(x=self.x + other, y=self.y + other)

    def __sub__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x - other.x, y=self.y - other.y)

        return Vec2.from_cartesian(x=self.x - other, y=self.y - other)

    def __mul__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_polar(angle=self.angle + other.angle, length=self.length * other.length)

        return Vec2.from_cartesian(x=self.x * other, y=self.y * other)

    def __truediv__(self, other):
        return Vec2.from_cartesian(x=self.x / other, y=self.y / other)

    # internal functions
    def __update(self, calc_from):
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

    def __abs__(self):
        return np.sqrt(self.x**2 + self.y**2)

    def __repr__(self):
        return f"<\n" \
               f"\tVec2:\n" \
               f"\tx:{self.x}\ty:{self.y}\n" \
               f"\tangle:{self.angle}\tlength:{self.length}\n" \
               f">"

    # static methods.
    # creation of new instances
    @staticmethod
    def from_cartesian(x, y) -> "Vec2":
        p = Vec2()
        p.xy = x, y

        return p

    @staticmethod
    def from_polar(angle, length) -> "Vec2":
        p = Vec2()
        p.polar = angle, length

        return p

    @staticmethod
    def from_dict(dictionary: dict) -> "Vec2":
        if "x" in dictionary and "y" in dictionary:
            return Vec2.from_cartesian(x=dictionary["x"], y=dictionary["y"])

        elif "angle" in dictionary and "length" in dictionary:
            return Vec2.from_polar(angle=dictionary["angle"], length=dictionary["length"])

        else:
            raise KeyError("either (x & y) or (angle & length) must be in dict!")

    @staticmethod
    def normalize_angle(value: float) -> float:
        while value > 2 * PI:
            value -= 2 * PI

        while value < 0:
            value += 2 * PI

        return value


class BetterDict:
    """
    each element is also accessible with instance.element
    """
    def __init__(self, **initial) -> None:
        for key, value in initial.items():
            setattr(self, key, value)

    def __setitem__(self, key: str, value: tp.Any) -> None:
        setattr(self, key, value)

    def __getitem__(self, item: str) -> tp.Any:
        return self.__dict__[item]

    def __delitem__(self, key) -> None:
        delattr(self, key)
