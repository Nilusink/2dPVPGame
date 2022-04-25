"""
Author:
Nilusink
"""
from core.new_types import Vec2
import pygame as pg


class _Game:
    screen: pg.Surface
    lowest_layer: pg.Surface
    middle_layer: pg.Surface
    top_layer: pg.Surface
    font: pg.font.Font
    __registered_objects: list[pg.sprite.Sprite]
    __last_pressed_keys: dict[str, bool]
    __pressed_keys: dict[str, bool]
    __platforms: list[dict]
    __world_config: dict
    __last: float
    def __init__(self, world_path: str, window_size: tuple[int, int] = ...) -> None: ...
    def load_world(self, world_path: str) -> None: ...
    def draw_world(self) -> None: ...
    def on_floor(self, point: Vec2) -> bool: ...
    def is_pressed(self, key: str) -> bool: ...
    def was_last_pressed(self, key: str) -> bool: ...
    def update(self) -> None: ...
    @staticmethod
    def end() -> None: ...


Game: _Game
