"""
Author:
Nilusink
"""
from core.new_types import Vec2
import pygame as pg
import typing as tp


def print_traceback(func: tp.Callable) -> tp.Callable:
    def wrapper(*args, **kwargs):
        ...


class _Game:
    screen: pg.Surface
    lowest_layer: pg.Surface
    middle_layer: pg.Surface
    top_layer: pg.Surface
    font: pg.font.Font
    world_bounds: Vec2
    __to_blit: list[pg.Surface, pg.Surface, Vec2]
    __registered_objects: list[pg.sprite.Sprite]
    __last_pressed_keys: dict[str, bool]
    __pressed_keys: dict[str, bool]
    __platforms: list[dict]
    __text_to_rend: list[tuple[str, Vec2]]
    __world_config: dict
    __last: float
    def __init__(self, world_path: str, window_size: tuple[int, int] = ...) -> None: ...
    def load_world(self, world_path: str) -> None: ...
    def draw_world(self) -> None: ...
    def print(self, text: str, position: Vec2, surface: pg.Surface, color: tuple[float, float, float, float]) -> None: ...
    def _render_text(self) -> None: ...
    def on_floor(self, point: Vec2) -> bool: ...
    def is_pressed(self, key: str) -> bool: ...
    def was_last_pressed(self, key: str) -> bool: ...
    def update(self) -> None: ...
    def in_loop(self, function: tp.Callable, *args, **kwargs) -> None: ...
    def blit(self, surface: pg.Surface, image: pg.Surface, position: Vec2) -> tuple[pg.Surface, pg.Surface, Vec2]: ...
    def unblit(self, element: tuple[pg.Surface, pg.Surface, Vec2]) -> None: ...
    @staticmethod
    def end() -> None: ...


Game: _Game


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
    def get_by_id(self, id: int): ...


class _GravityAffected(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    position: Vec2
    """
    def calculate_gravity(self, delta: float) -> None: ...


class _FrictionXAffected(pg.sprite.Group):
    def calculate_friction(self, delta: float) -> None: ...


class _FrictionAffected(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    """
    def calculate_friction(self, delta: float) -> None: ...


class _FollowsMouse(pg.sprite.Group):
    """
    required methods / variables:
    position: Vec2
    """
    def update(self, *args, **kwargs) -> None: ...


class _CollisionDestroyed(pg.sprite.Group):
    """
    required methods / variables
    damage: float (optional, use if collision should damage the other object)
    hp: float (optional, sprite should either have damage or hp (or both))
    hit(damage: float) -> None
    kill() -> None
    """
    def update(self) -> None: ...
    def box_collide(self, other: pg.sprite.Sprite) -> tp.Iterator: ...


class _HasBars(pg.sprite.Group):
    """
    required methods / variables:
    hp: float
    max_hp: float
    weapon: Bullet
    cooldown: float
    """
    def draw(self, surface: pg.Surface) -> None: ...


class _WallBouncer(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    position: Vec2
    """
    def update(self) -> None: ...


# create instances
Players: _Players
Bullets: _Bullets
Rockets: _Rockets
Updated: _Updated
HasBars: _HasBars
WallBouncer: _WallBouncer
FollowsMouse: _FollowsMouse
NetworkUpdated: _NetworkUpdated
GravityAffected: _GravityAffected
UpdatesToNetwork: _UpdatesToNetwork
FrictionAffected: _FrictionAffected
FrictionXAffected: _FrictionXAffected
CollisionDestroyed: _CollisionDestroyed