"""
Author:
Nilusink
"""
from core.groups import *


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


class Bullet(pg.sprite.Sprite):
    parent: pg.sprite.Sprite
    character_path: str
    last_angle: float
    cooldown: float
    velocity: Vec2
    damage: float
    speed: float
    rect: pg.Rect
    __original_image: pg.Surface
    __position: Vec2
    def __init__(self, position: Vec2, velocity: Vec2, parent: pg.sprite.Sprite) -> None: ...
    @property
    def position(self) -> Vec2: ...
    @property
    def on_ground(self) -> bool:...
    @property
    def out_of_bounds(self) -> bool:...
    def update(self, delta: float) -> None:...
    def hit(self, _damage: float) -> None:...


class AK47(Bullet):
    character_path: str
    cooldown: float
    damage: float
    speed: float
    _size: int


class Rocket(Bullet):
    character_path: str
    cooldown: float
    damage: float
    speed: float
    _size: int
    hp: float
    def __init__(self, *args, **kwargs) -> None: ...
    def hit(self, damage: float) -> None: ...


class Sniper(Bullet):
    character_path: str
    cooldown: float
    damage: float
    speed: float
    _size: int


class Player(pg.sprite.Sprite):
    controls: tuple[str, str, str]
    parent: pg.sprite.Sprite
    character_path: str
    bullet_offset: Vec2
    jump_speed: float
    image: pg.Surface
    max_speed: float
    position: Vec2
    velocity: Vec2
    shoots: bool
    hp: float
    __weapon_indicator: WeaponIndicator
    __weapon_index: int = 0
    __available_weapons: list
    __weapon: tp.Type[Bullet]
    __cooldown: list[float]
    __bullets: list[Bullet]
    __groups: list | tuple
    __max_hp: float
    __facing: str
    __spawn: Vec2
    __size: int
    def __init__(self,
                 spawn_point: Vec2,
                 *groups,
                 velocity: Vec2 = ...,
                 controls: tuple[str, str, str] = ("", "", ""),
                 shoots: bool = False
                 ) -> None: ...
    @property
    def weapon(self) -> tp.Type[Bullet]: ...
    @weapon.setter
    def weapon(self, weapon: tp.Type[Bullet]) -> None: ...
    @property
    def available_weapons(self) -> tuple: ...
    @property
    def weapon_index(self) -> int: ...
    @weapon_index.setter
    def weapon_index(self, index: int) -> None: ...
    @property
    def size(self) -> int: ...
    @property
    def facing(self) -> str: ...
    @facing.setter
    def facing(self, direction: str) -> None: ...
    @property
    def on_ground(self) -> bool: ...
    @property
    def max_hp(self) -> float: ...
    @property
    def cooldown(self) -> float: ...
    @cooldown.setter
    def cooldown(self, value: float) -> None: ...
    def update_rect(self) -> None: ...
    def update(self, delta: float) -> None: ...
    def shoot(self, direction: Vec2) -> None: ...
    def hit(self, damage: float) -> None: ...
    def revive(self) -> None: ...


class Scope(pg.sprite.Sprite):
    character_path: str = "../images/weapons/scope.png"
    image: pg.Surface
    position: Vec2
    rect: pg.Rect
    size: int
    def __init__(self): ...
    def update(self, _delta: float) -> None: ...


class WeaponIndicator(pg.sprite.Sprite):
    character_path: str = "./images/weapons/WEAPON.png"
    scale: tuple[int, int]
    images: pg.surface
    position: Vec2
    rect: pg.Rect
    __weapon: tp.Type[Bullet]
    def __init__(self, position: Vec2, weapon: tp.Type[Bullet]) -> None: ...
    @property
    def weapon(self) -> tp.Type[Bullet]: ...
    @weapon.setter
    def weapon(self, weapon: tp.Type[Bullet]) -> None: ...
