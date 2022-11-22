"""
Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor as Pool
from traceback import format_exc
from contextlib import suppress
from core.new_types import Vec2
import core.config as config
import pygame as pg
import typing as tp
import numpy as np
import string
import json
import time
import os


# Fixes errors (actually), keep False
_ERROR_FIXER: bool = False


def print_traceback(func: tp.Callable) -> tp.Callable:
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)

        except Exception:
            print(f"\nexception in {func}:\n {format_exc()}\n")
            raise

    return wrapper


class _Game:
    running: bool = True
    world_bounds: Vec2 = Vec2.from_cartesian(np.inf, np.inf)

    def __init__(self, world_path: str, window_size: tuple[int, int] = ...):
        # initialize pygame
        pg.init()
        pg.font.init()

        if window_size is ...:
            screen_info = pg.display.Info()
            window_size = (screen_info.current_w, screen_info.current_h)

        # create window
        self.times = []
        self.times_values = []
        self.times_Values2 = []
        self.screen = pg.display.set_mode(window_size, pg.SCALED)
        self.lowest_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.middle_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.top_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.font = pg.font.SysFont(None, 24)
        pg.display.set_caption("Gayme")
        # pg.mouse.set_visible(False)

        # later used variables
        self.__registered_objects: list[pg.sprite.Sprite] = []

        self.__pressed_keys: dict[str, bool] = {}
        self.__last_pressed_keys: dict[str, bool] = {}

        self.__last = time.perf_counter()
        self.__last_calculate = time.perf_counter_ns()

        self.__platforms: list[dict] = []
        self.__world_config: dict = {}
        self.__to_blit: list[tuple[pg.Surface, pg.Surface, Vec2]] = []
        self.__to_loop: list[tuple[tp.Callable, list, dict]] = []

        self.__text_to_rend: list[tuple[str, Vec2, pg.Surface, tuple[float, float, float, float]]] = []

        # Threading
        # pool init
        self.__pool = Pool(max_workers=100)

        # create own thread for calculating stuff
        self.__pool.submit(self.calculate_stuff)

        self.load_world(world_path)

    def print(self, text: str, position: Vec2, surface: pg.Surface, color: tuple[float, float, float, float]) -> None:
        self.__text_to_rend.append((text, position, surface, color))

    def _render_text(self) -> None:
        for element in self.__text_to_rend.copy():
            self.__text_to_rend.remove(element)
            surf = self.font.render(element[0], False, element[3])
            element[2].blit(surf, element[1].xy)

    def load_world(self, world_path: str) -> None:
        if not os.path.exists(world_path):
            raise FileNotFoundError(f"No such file or directory: {world_path}")

        conf: dict = json.load(open(world_path, "r"))
        self.__platforms = conf["platforms"]
        self.world_bounds = Vec2.from_cartesian(*conf["bounds"])
        conf.pop("platforms")
        conf.pop("bounds")
        self.__world_config = conf

    def draw_world(self) -> None:
        self.lowest_layer.fill(self.__world_config["background"])
        for platform in self.__platforms:
            x, y = platform["pos"]
            x *= config.const.PIXELS_PER_METER
            y *= config.const.PIXELS_PER_METER
            width, height = platform["size"]
            width *= config.const.PIXELS_PER_METER
            height *= config.const.PIXELS_PER_METER
            pg.draw.rect(self.lowest_layer, platform["color"], pg.Rect(x, y, width, height))

    def on_floor(self, point: Vec2):
        """
        takes a point and checks if it is on the floor
        """
        for platform in self.__platforms:
            x, y = platform["pos"]
            width, height = platform["size"]
            if all([
                x < point.x < x + width,
                y < point.y < y + height
            ]):
                return True
        return False

    def is_pressed(self, key: str) -> bool:
        return key in self.__pressed_keys and self.__pressed_keys[key]

    def was_last_pressed(self, key: str) -> bool:
        return key in self.__last_pressed_keys and self.__last_pressed_keys[key]

    @print_traceback
    def calculate_stuff(self, loop: bool = True) -> None:
        while not _ERROR_FIXER:
            pass

        def johnathan():
            now = time.perf_counter_ns()
            delta = now - self.__last_calculate
            self.__last_calculate = now

            delta /= 1e9

            # update Updated group
            Updated.update(delta)

            # calculate stuff
            GravityAffected.calculate_gravity(delta)
            FrictionAffected.calculate_friction(delta)
            FrictionXAffected.calculate_friction(delta)
            WallBouncer.update()

            # check for collisions
            CollisionDestroyed.update()

            self.times.append([
                now,
                time.perf_counter_ns()-now,
                len(Bullets.sprites())
            ])
            # self.times_values.append()
            # self.times_values.append()

        if not loop:
            johnathan()
            return

        while self.running:
            johnathan()

        with open("out.json", "w") as out:
            json.dump({
                "x": [el[0] for el in self.times],
                "y1": [el[1] for el in self.times],
                "y2": [el[2] for el in self.times]
            }, out)

    def update(self) -> None:
        """
        calls updates on all registered objects n' stuff
        also handles key-presses
        """
        # clear screen
        self.screen.fill((0, 0, 0, 0))
        self.lowest_layer.fill((0, 0, 0, 0))
        self.middle_layer.fill((0, 0, 0, 0))
        self.top_layer.fill((0, 0, 0, 0))

        # stuff
        now = time.perf_counter()
        delta = now - self.__last

        self.__last_pressed_keys = self.__pressed_keys.copy()

        su = sd = False
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    self.end()

                case pg.MOUSEBUTTONDOWN:
                    match event.button:
                        case 4:
                            su = True

                        case 5:
                            sd = True

                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_ESCAPE:
                            self.end()

        self.__pressed_keys["scroll_up"] = su
        self.__pressed_keys["scroll_down"] = sd

        # handle key-presses
        _keys = pg.key.get_pressed()
        to_check = list(string.ascii_lowercase)
        to_check += list(string.digits)
        to_check += [
            "SPACE",
            "LEFT",
            "RIGHT",
            "UP"
        ]

        for key in to_check:
            self.__pressed_keys[key] = eval(f"_keys[pg.K_{key}]")

        # put to mouse
        FollowsMouse.update(self.top_layer)

        # self.calculate_stuff(loop=False)

        # draw health bars
        HasHP.draw(self.top_layer)
        HasBars.draw(self.top_layer)

        # draw updated objects and world
        for element in self.__to_blit.copy():
            element[0].blit(element[1], (element[2].x, element[2].y))

        self.draw_world()

        Updated.draw(self.middle_layer)

        lo = self.__to_loop.copy()
        self.__to_loop.clear()
        for element in lo:
            element[0](*element[1], **element[2])

        # draw layers
        self._render_text()
        self.screen.blit(self.lowest_layer, (0, 0))
        self.screen.blit(self.middle_layer, (0, 0))
        self.screen.blit(self.top_layer, (0, 0))

        self.__last = now

    def in_loop(self, function: tp.Callable, *args, **kwargs) -> None:
        self.__to_loop.append((function, args, kwargs))

    def blit(self, surface: pg.Surface, image: pg.Surface, position: Vec2) -> tuple[pg.Surface, pg.Surface, Vec2]:
        self.__to_blit.append((surface, image, position))
        return surface, image, position

    def unblit(self, element: tuple[pg.Surface, pg.Surface, Vec2]) -> None:
        self.__to_blit.remove(element)

    def end(self) -> None:
        print(f"quitting...")
        self.running = False
        pg.quit()
        exit()


# should be the only instance of the class
Game = _Game("./worlds/world_test.json", config.const.WINDOW_SIZE)


# groups
class _Players(pg.sprite.Group):
    ...


class _Bullets(pg.sprite.Group):
    ...


class _Rockets(pg.sprite.Group):
    ...


class _Updated(pg.sprite.Group):
    ...


class _UpdatesToNetwork(pg.sprite.Group):
    # required functions / variables:
    # events: list[Event]
    ...


class _NetworkUpdated(pg.sprite.Group):
    def get_by_id(self, obj_id: int):
        for sprite in self.sprites():
            if sprite.id == obj_id:
                return sprite


class _GravityAffected(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    position: Vec2
    """
    def calculate_gravity(self, delta: float) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite: tp.Any
                if not sprite.on_ground or sprite.velocity.y < 0:
                    sprite.acceleration.y = config.const.g
                    continue

                while sprite.on_ground:
                    sprite.position.y -= 0.01
                sprite.position.y += 0.01

                sprite.velocity.y = 0


class _FrictionXAffected(pg.sprite.Group):
    def calculate_friction(self, delta: float) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite: tp.Any
                sprite.velocity.x *= 1 - (0.5 * delta)


class _FrictionAffected(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    """
    def calculate_friction(self, delta: float) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite: tp.Any
                sprite.velocity.length -= sprite.velocity.length * delta * 0.01


class _FollowsMouse(pg.sprite.Group):
    """
    required methods / variables:
    position: Vec2
    """
    def update(self, *args, **kwargs) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite: tp.Any
                mouse_pos = pg.mouse.get_pos()
                sprite.position = Vec2.from_cartesian(*mouse_pos)


class _CollisionDestroyed(pg.sprite.Group):
    """
    required methods / variables
    damage: float (optional, use if collision should damage the other object)
    hp: float (optional, sprite should either have damage or hp (or both))
    hit(damage: float) -> None
    kill() -> None
    """
    def update(self) -> None:
        calculated: list[set] = []
        for sprite in self.sprites():
            with suppress(AttributeError):
                for other in self.sprites():
                    sprite: tp.Any
                    other: tp.Any
                    if not (sprite in Bullets and other in Bullets):
                        if self.size_collide(sprite, other):
                            if not {other, other.parent} & {sprite, sprite.parent} and {sprite, other} not in calculated:
                                try:
                                    dmg = other.damage

                                except AttributeError:
                                    dmg = 0

                                hp = sprite.hp
                                sprite.hit(dmg)
                                if dmg != 0:
                                    other.hit_someone(target_hp=hp)

                    calculated.append({sprite, other})

    @staticmethod
    def size_collide(sprite1, sprite2) -> bool:
        # check for the first sprite to be in the second
        collision_distance = sprite1.size + sprite2.size
        return (sprite1.position_center - sprite2.position_center).length <= collision_distance

    def box_collide(self, other: pg.sprite.Sprite) -> tp.Iterator:
        for sprite in self.sprites():
            if pg.sprite.collide_rect(sprite, other) and sprite is not other:
                yield sprite


class _HasBars(pg.sprite.Group):
    """
    required methods / variables:
    hp: float
    max_hp: float
    weapon: Bullet
    cooldown: float
    """
    def draw(self, surface: pg.Surface) -> None:
        for sprite in self.sprites():
            with suppress(KeyError):
                sprite: tp.Any
                bar_height = sprite.screen_size / 10

                # draw health bar
                max_len = sprite.screen_size
                now_len = (sprite.hp / sprite.max_hp) * max_len

                bar_start = sprite.screen_position.copy()
                bar_start.x -= sprite.screen_size / 2

                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(*bar_start.xy, max_len, bar_height)
                )
                pg.draw.rect(
                    surface,
                    (0, 255, 0, 255),
                    pg.Rect(*bar_start.xy, now_len, bar_height)
                )

                # draw mag / reload bar
                mag_n, mag_v = sprite.weapon_handler.get_mag_state(1000)
                now_len = (mag_n / 1000) * max_len
                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(bar_start.x, bar_start.y + 1.5 * bar_height, max_len if now_len else 0, bar_height)
                )
                pg.draw.rect(
                    surface,
                    (155, 155, 255, 255),
                    pg.Rect(bar_start.x, bar_start.y + 1.5 * bar_height, now_len, bar_height)
                )

                # draw mag text
                text_pos = bar_start.copy()
                text_pos.y += 1.5 * bar_height
                Game.print(str(mag_v), text_pos, Game.top_layer, (0, 0, 0, 255))

                # draw cooldown bar
                now_len = (sprite.weapon_handler.current_cooldown / sprite.weapon.cooldown) * max_len
                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(bar_start.x, bar_start.y + 2 * 1.5 * bar_height, max_len if now_len else 0, bar_height)
                )
                pg.draw.rect(
                    surface,
                    (155, 155, 255, 255),
                    pg.Rect(bar_start.x, bar_start.y + 2 * 1.5 * bar_height, now_len, bar_height)
                )


class _HasHP(pg.sprite.Group):
    def draw(self, surface: pg.Surface) -> None:
        for sprite in self.sprites():
            with suppress(KeyError):
                sprite: tp.Any
                bar_height = 2

                # don't draw if full hp
                if sprite.hp == sprite.max_hp:
                    continue

                # draw health bar
                max_len = 10
                now_len = (sprite.hp / sprite.max_hp) * max_len

                bar_start = sprite.screen_position.copy()
                bar_start.x -= sprite.screen_size / 2

                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(*bar_start.xy, max_len, bar_height)
                )
                pg.draw.rect(
                    surface,
                    (0, 255, 0, 255),
                    pg.Rect(*bar_start.xy, now_len, bar_height)
                )


class _WallBouncer(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    position: Vec2
    """
    def update(self) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite: tp.Any
                if 0 > sprite.position.x:
                    sprite.velocity.x = abs(sprite.velocity.x)

                elif sprite.position.x > config.const.WINDOW_SIZE[0]:
                    sprite.velocity.x = -abs(sprite.velocity.x)

                if 0 > sprite.position.y:
                    sprite.velocity.y = abs(sprite.velocity.y)

                elif sprite.position.y > config.const.WINDOW_SIZE[1]:
                    sprite.velocity.y = -abs(sprite.velocity.y)


# create instances
HasHP = _HasHP()
Players = _Players()
Bullets = _Bullets()
Rockets = _Rockets()
Updated = _Updated()
HasBars = _HasBars()
WallBouncer = _WallBouncer()
FollowsMouse = _FollowsMouse()
NetworkUpdated = _NetworkUpdated()
GravityAffected = _GravityAffected()
UpdatesToNetwork = _UpdatesToNetwork()
FrictionAffected = _FrictionAffected()
FrictionXAffected = _FrictionXAffected()
CollisionDestroyed = _CollisionDestroyed()


_ERROR_FIXER = True
