"""
Author:
Nilusink
"""
from contextlib import suppress
from core.new_types import Vec2
import core.config as config
import pygame as pg
import typing as tp


# groups
class _Players(pg.sprite.Group):
    ...


class _Updated(pg.sprite.Group):
    ...


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
                    sprite.velocity.y += config.const.g * delta
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
        for sprite in self.sprites():
            with suppress(AttributeError):
                for other in self.sprites():
                    sprite: tp.Any
                    other: tp.Any
                    if all([
                            pg.sprite.collide_mask(sprite, other),
                            other != sprite,
                            other.parent != sprite,
                            sprite.parent != other
                    ]):
                        # print(f"collision: {sprite}, {other}")
                        try:
                            dmg = other.damage

                        except AttributeError:
                            dmg = 0

                        hp = sprite.hp
                        sprite.hit(dmg)
                        if dmg != 0:
                            other.hit_someone(target_hp=hp)

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
            with suppress(AttributeError):
                sprite: tp.Any
                bar_height = 10

                # draw health bar
                max_len = sprite.size
                now_len = (sprite.hp / sprite.max_hp) * max_len

                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(sprite.position.x, sprite.position.y, max_len, bar_height)
                )
                pg.draw.rect(
                    surface,
                    (0, 255, 0, 255),
                    pg.Rect(sprite.position.x, sprite.position.y, now_len, bar_height)
                )

                # draw reload bar
                now_len = (sprite.cooldown / sprite.weapon.cooldown) * max_len
                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(sprite.position.x, sprite.position.y + 1.5 * bar_height, max_len if now_len else 0, bar_height)
                )
                pg.draw.rect(
                    surface,
                    (155, 155, 255, 255),
                    pg.Rect(sprite.position.x, sprite.position.y + 1.5 * bar_height, now_len, bar_height)
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
Players = _Players()
Updated = _Updated()
GravityAffected = _GravityAffected()
FrictionXAffected = _FrictionXAffected()
FrictionAffected = _FrictionAffected()
CollisionDestroyed = _CollisionDestroyed()
FollowsMouse = _FollowsMouse()
HasBars = _HasBars()
WallBouncer = _WallBouncer()
