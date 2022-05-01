"""
Author:
Nilusink
"""
import configparser
from dataclasses import dataclass
from threading import Timer
from random import randint
import numpy as np
import time

from core.animations import play_animation
from core.basegame import Game
from core.groups import *

# Events
# Event types
SHOT: int = 0
BULLET_UPDATE: int = 1
PLAYER_UPDATE: int = 2


# Event class
@dataclass(frozen=True)
class Event:
    type: int

    def to_dict(self) -> dict[str, str]:
        """
        convert the event to a dict
        """
        out = {
            "name": type(self).__name__,
        }
        for key, item in self.__dict__.items():
            if issubclass(type(item), Vec2):
                out[key] = item.to_dict()

            elif issubclass(type(item), Bullet):
                out[key] = type(item).__name__

            else:
                out[key] = item

        return out


@dataclass(frozen=True)
class Shot(Event):
    parent: "Player"
    position: Vec2
    direction: Vec2
    weapon: tp.Type["Bullet"]
    id: int


@dataclass(frozen=True)
class BulletUpdate(Event):
    position: Vec2
    velocity: Vec2
    damage: float
    id: int


@dataclass(frozen=True)
class PlayerUpdate(Event):
    position: Vec2
    velocity: Vec2
    damage: float
    id: int


# Weapons
class Bullet(pg.sprite.Sprite):
    reload_time: float
    cooldown: float
    mag_size: int
    damage: float
    speed: float
    _size: int = 0
    parent: pg.sprite.Sprite
    character_path: str
    last_angle: float
    velocity: Vec2
    rect: pg.Rect
    _original_image: pg.Surface
    _position: Vec2
    id: int

    def __init__(self, position: Vec2, direction: Vec2, parent: pg.sprite.Sprite, initial_velocity: Vec2 = Vec2()):
        super().__init__()
        self._position = position
        self.velocity = direction
        self.last_angle = 0
        self.parent = parent

        self.cooldown: float
        self.damage: float
        self.speed: float

        self.velocity.length = self.speed
        self.velocity += initial_velocity.split_vector(direction)[0]

        img = pg.image.load(self.character_path)
        img = pg.transform.scale(img, (self._size, self._size))
        self._original_image = img

        self.image = pg.transform.rotate(self._original_image, -self.velocity.angle * (180 / config.const.PI))
        self.last_angle = self.velocity.angle

        self.rect = pg.Rect(
            self._position.x - self._size / 2,
            self._position.y - self._size / 2,
            self._size,
            self._size
        )
        self.id = randint(0, 1_000_000_000)

        self.add(Updated, CollisionDestroyed, FrictionAffected, GravityAffected, WallBouncer)

    @property
    def position(self) -> Vec2:
        return self._position

    @property
    def on_ground(self) -> bool:
        return Game.on_floor(self._position)

    @property
    def out_of_bounds(self) -> bool:
        return all([
            not -200 < self._position.x < config.const.WINDOW_SIZE[0] + 200,
            not -200 < self._position.y < config.const.WINDOW_SIZE[1] + 200,
        ])

    def get_nearest_player(self, exclude_parent: bool) -> tp.Union["Player", None]:
        closest_distance: float = np.inf
        closest_player: Player | None = None
        for player in Players.sprites():
            if exclude_parent and player is self.parent:
                continue

            player: Player
            dist = abs((self._position - player.position).length)
            if dist < closest_distance:
                closest_player = player
                closest_distance = dist

        return closest_player

    def update(self, delta: float) -> None:
        self._update(delta)

    def _update(self, delta: float) -> None:
        self._position += self.velocity * delta

        if self.out_of_bounds or self.on_ground:
            self.on_death()

        self.image = pg.transform.rotate(self._original_image, -self.velocity.angle * (180 / config.const.PI))
        self.last_angle = self.velocity.angle

        self.rect = pg.Rect(
            self._position.x - self._size / 2,
            self._position.y - self._size / 2,
            self._size,
            self._size
        )

    def hit(self, _damage: float) -> None:
        self.on_death()

    def hit_someone(self, target_hp: float) -> None:
        self.damage -= target_hp
        if self.damage <= 0:
            self.on_death()

    def on_death(self) -> None:
        self.kill()


class AK47(Bullet):
    character_path: str = "./images/weapons/bullet.png"
    reload_time = config.const.BULLET_RELOAD_TIME
    mag_size = config.const.BULLET_MAG_SIZE
    cooldown = config.const.BULLET_COOLDOWN
    damage = config.const.BULLET_DAMAGE
    speed = config.const.BULLET_SPEED
    _size = 16


class Rocket(Bullet):
    explosion_animation: str = "./images/animations/explosion/"
    character_path: str = "./images/weapons/rocket.png"
    reload_time = config.const.ROCKET_RELOAD_TIME
    mag_size = config.const.ROCKET_MAG_SIZE
    cooldown = config.const.ROCKET_COOLDOWN
    damage = config.const.ROCKET_DAMAGE
    speed = config.const.ROCKET_SPEED
    _size = 64
    hp = 2

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.on_death()

    def hit_someone(self, target_hp: float) -> None:
        self.on_death()

    def on_death(self) -> None:
        size = Vec2.from_cartesian(100, 100)
        play_animation(
            directory=self.explosion_animation,
            position=self.position.copy(),
            size=size,
            surface=Game.top_layer,
            delay=.05
        )

        hit_box = pg.sprite.Sprite()
        hit_box.rect = pg.rect.Rect(
            self.position.x - size.x / 2,
            self.position.y - size.y / 2,
            size.x,
            size.y
        )

        for sprite in CollisionDestroyed.box_collide(hit_box):
            if sprite is not self and not issubclass(type(sprite), Rocket):
                sprite.hit(self.damage)

        self.kill()


class HomingRocket(Rocket):
    acceleration: float = 5
    speed = config.const.HOMING_ROCKET_SPEED
    damage = config.const.HOMING_ROCKET_DAMAGE
    cooldown = config.const.HOMING_ROCKET_COOLDOWN
    mag_size = config.const.HOMING_ROCKET_MAG_SIZE
    reload_time = config.const.HOMING_ROCKET_RELOAD_TIME
    character_path: str = "./images/weapons/homingrocket.png"
    __grad_per_sec: float = 60
    __rad_per_sec: float
    __events: list[Event]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__rad_per_sec = self.__grad_per_sec * (config.const.PI / 180)

        self.__events = []

        self._id = randint(0, 1_000_000_000)

        self.add(UpdatesToNetwork)
        self.remove(GravityAffected)

    @property
    def events(self) -> list[Event]:
        tmp = self.__events.copy()
        self.__events.clear()
        return tmp

    def update(self, delta: float) -> None:
        target: Player = self.get_nearest_player(exclude_parent=True)
        if target:
            position_delta = target.position_center - self.position
            angle_delta = self.velocity.angle - position_delta.angle

            while angle_delta > 2*config.const.PI:
                angle_delta -= 2*config.const.PI

            end = self.position + Vec2.from_polar(angle=angle_delta+self.velocity.angle, length=50)
            pg.draw.line(Game.top_layer, (255, 0, 0, 255), self.position.xy, end.xy)

            end = self.position + Vec2.from_polar(angle=angle_delta, length=50)
            pg.draw.line(Game.top_layer, (0, 0, 255, 255), self.position.xy, end.xy)

            sign = 1
            if angle_delta > 0.001:
                sign = -angle_delta / abs(angle_delta)

            to_change = sign * self.__rad_per_sec * (delta / config.const.T_MULT)

            if angle_delta > config.const.PI:
                to_change *= -1

            end = self.position + Vec2.from_polar(angle=to_change, length=700)
            pg.draw.line(Game.top_layer, (0, 255, 0, 255), self.position.xy, end.xy)

            self.velocity.angle += to_change

        self.velocity.length += self.acceleration * delta

        self._update(delta)


class Sniper(Bullet):
    character_path: str = "./images/weapons/bullet.png"
    reload_time = config.const.SNIPER_RELOAD_TIME
    mag_size = config.const.SNIPER_MAG_SIZE
    cooldown = config.const.SNIPER_COOLDOWN
    damage = config.const.SNIPER_DAMAGE
    speed = config.const.SNIPER_SPEED
    _size = 32


class WeaponHandler:
    inaccuracy_resolution: int = 1000
    __last_shot: float
    __current_mag: dict[int]
    __current_reload: dict[float]
    __weapon: tp.Type[Bullet]
    __current_cooldown: dict[float]
    __parent: pg.sprite.Sprite

    def __init__(self, parent: pg.sprite.Sprite, weapon: tp.Type[Bullet]):
        self.__parent = parent
        self.__weapon = weapon

        self.__current_reload = 0
        self.__current_cooldown = 0
        self.__current_mag = weapon.mag_size

        self.__last_shot = time.time()

    def shoot(self, direction: Vec2, inaccuracy: float) -> None:
        """
        :param direction: the direction to shoot at
        :param inaccuracy: in rad, 0 to switch off
        """
        time_d = time.time() - self.__last_shot
        self.__current_cooldown -= time_d
        self.__current_reload -= time_d

        if self.__current_reload <= 0 and self.__current_cooldown <= 0:
            offset = (randint(-self.inaccuracy_resolution, self.inaccuracy_resolution) / self.inaccuracy_resolution)
            offset *= inaccuracy
            direction.angle += inaccuracy
            direction.length = 100

            pos = direction
            pos += self.__parent.position_center
            self.__weapon(pos, direction, self.__parent, self.__parent.velocity)


# Player kinds
class Player(pg.sprite.Sprite):
    # public
    hp: float
    name: str
    shoots: bool
    velocity: Vec2
    position: Vec2
    respawns: bool
    image: pg.Surface
    mouse_center: Vec2
    bullet_offset: Vec2
    parent: pg.sprite.Sprite
    controls: tuple[str, str, str, str]
    max_speed: float = config.const.MAX_SPEED
    jump_speed: float = config.const.JUMP_SPEED
    character_path: str = "./images/characters/amogus/amogusSIZEDIRECTION.png"

    # private
    __weapon_indicator: "WeaponIndicator"
    __max_hp: float = config.const.MAX_HP
    __on_ground_override: bool = False
    __available_weapons: list
    __weapon: WeaponHandler
    __weapon_index: int = 0
    __bullets: list[Bullet]
    __cooldown: list[float]
    __facing: str = "right"
    __groups: list | tuple
    __events: list[dict]
    __max_hp: float
    __spawn: Vec2
    __size: int = 32

    def __init__(self,
                 spawn_point: Vec2,
                 *groups_,
                 velocity: Vec2 = ...,
                 controls: tuple[str, str, str, str] = ("", "", "", ""),
                 shoots: bool = False,
                 respawns: bool = False,
                 name: str = ""
                 ) -> None:

        if velocity is ...:
            velocity = Vec2()

        # init mutable defaults
        self.__events = []
        self.__bullets = []

        super().__init__(*groups_)
        # weapon config
        self.__weapon_index: int = 0
        self.__available_weapons: tuple = (
            AK47,
            Sniper,
            Rocket,
            HomingRocket
        )
        w = self.__available_weapons[self.__weapon_index]
        self.__weapon = WeaponHandler(self, w)

        self.mouse_center = Vec2.from_cartesian(*config.const.WINDOW_SIZE) / 2

        # player meta
        self.__spawn = spawn_point
        self.position = Vec2.from_cartesian(spawn_point.x, spawn_point.y)
        self.velocity = velocity
        self.controls = controls
        self.respawns = respawns
        self.shoots = shoots
        self.name = name

        # player config
        self.hp = self.__max_hp

        self.bullet_offset: Vec2 = Vec2.from_cartesian(
            x=0,
            y=-self.size
        )

        self.parent: pg.sprite.Sprite = self

        self.__cooldown: list[float] = [0] * len(self.available_weapons)

        image = pg.image.load(self.character_path
                              .replace("SIZE", str(self.__size))
                              .replace("DIRECTION", self.facing)
                              )
        self.image = pg.transform.scale(image, (self.__size, self.__size))
        self.update_rect()

        # add to the player group
        self.__groups = [Players, Updated, GravityAffected, FrictionXAffected, CollisionDestroyed, HasBars]
        self.add(*self.__groups)

        self.__weapon_indicator: WeaponIndicator = ...
        if self.shoots:
            self.__weapon_indicator = WeaponIndicator(Vec2.from_cartesian(0, 0), self.weapon)

    @property
    def position_center(self) -> Vec2:
        return self.position + Vec2.from_cartesian(0, -self.size / 2)

    @property
    def events(self) -> list[dict]:
        tmp = self.__events.copy()
        self.__events.clear()
        return tmp

    @property
    def weapon(self) -> tp.Type[Bullet]:
        return self.__weapon.weapon

    @weapon.setter
    def weapon(self, weapon: tp.Type[Bullet]) -> None:
        if self.shoots:
            self.__weapon = weapon
            self.__weapon_indicator.weapon = weapon

    @property
    def available_weapons(self) -> tuple[tp.Type[Bullet]]:
        return self.__available_weapons

    @property
    def weapon_index(self) -> int:
        """
        state the index of the currently selected weapon out of available_weapons
        """
        return self.__weapon_index

    @weapon_index.setter
    def weapon_index(self, index: int) -> None:
        a_num = len(self.__available_weapons)
        while index >= a_num:
            index -= a_num

        while index < 0:
            index += a_num

        self.__weapon_index = index
        self.weapon = self.available_weapons[self.weapon_index]

    @property
    def size(self) -> int:
        return self.__size

    @property
    def facing(self) -> str:
        return self.__facing

    @facing.setter
    def facing(self, direction: str) -> None:
        direction = direction.lower()
        if direction not in "left, right":
            raise ValueError(f"Invalid Direction: \"{direction}\"")

        self.__facing = direction
        self.image = pg.image.load(self.character_path
                                   .replace("SIZE", str(self.size))
                                   .replace("DIRECTION", self.facing))
        match direction:
            case "right":
                self.bullet_offset.x = self.size

            case "left":
                self.bullet_offset.x = -self.size/2

    @property
    def on_ground(self) -> bool:
        return Game.on_floor(self.position) and self.velocity.y >= 0 and not self.__on_ground_override

    @property
    def max_hp(self) -> float:
        return self.__max_hp

    @property
    def cooldown(self) -> float:
        return self.__cooldown[self.weapon_index]

    @cooldown.setter
    def cooldown(self, value: float) -> None:
        self.__cooldown[self.weapon_index] = value

    def update_rect(self) -> None:
        self.rect = pg.Rect(self.position.x - self.size / 2, self.position.y - self.size, self.size, self.size)

    def update(self, delta: float) -> None:
        for i, cooldown in enumerate(self.__cooldown):
            self.__cooldown[i] = cooldown - delta / config.const.T_MULT if cooldown > 0 else 0

        if Game.is_pressed(self.controls[0]):
            self.velocity.x = self.max_speed  # if self.velocity.x < self.max_speed else self.max_speed

        if Game.is_pressed(self.controls[1]):
            self.velocity.x = -self.max_speed  # if -self.velocity.x > -self.max_speed else -self.max_speed

        if Game.is_pressed(self.controls[3]):
            self.__on_ground_override = True

        else:
            self.__on_ground_override = False

        if not Game.is_pressed(self.controls[0]) and not Game.is_pressed(self.controls[1]):
            self.velocity.x = 0

        if Game.is_pressed(self.controls[2]) and self.on_ground:
            self.velocity.y -= self.jump_speed

        # update aiming pointer
        if self.shoots:
            mouse_pos = pg.mouse.get_pos()
            mouse_pos = Vec2.from_cartesian(*mouse_pos)

            direction = mouse_pos - self.mouse_center
            direction.length = 60
            to = self.position_center + direction
            direction.length = 20
            start = self.position_center + direction
            pg.draw.line(Game.top_layer, (255, 0, 0, 255), start.xy, to.xy)

            if pg.mouse.get_pressed()[0]:
                if not self.cooldown:
                    self.shoot(direction)

        if Game.is_pressed("scroll_down"):
            self.weapon_index -= 1

        if Game.is_pressed("scroll_up"):
            self.weapon_index += 1

        # check if out of map
        if self.position.y > config.const.WINDOW_SIZE[1] + 200:
            self.on_death()

        # face the direction you're heading
        if self.velocity.x:
            if self.velocity.x > 0:
                self.facing = "right"

            elif self.velocity.x < 0:
                self.facing = "left"

        # update position
        self.position += self.velocity * delta

        # update on screen
        self.update_rect()

    def shoot(self, direction: Vec2) -> None:
        """
        shoot a bulletin the direction of the vector
        """
        # bullet spawner
        if self.shoots:
            pos = self.position_center
            pos += direction
            b = self.weapon(
                position=pos,
                direction=direction,
                parent=self,
                initial_velocity=self.velocity
            )
            self.__bullets.append(b)
            self.cooldown += b.cooldown

            self.__events.append({
                "type": SHOT,
                "weapon": self.weapon.__name__,
                "angle": direction.angle,
                "pos": {
                    "x": pos.x,
                    "y": pos.y,
                },
                "id": b.id
            })

    def hit(self, damage: float) -> None:
        self.hp -= damage
        if self.hp <= 0:
            self.on_death()

    def on_death(self) -> None:
        self.kill()
        if self.respawns:
            Timer(4.20, self.revive).start()

    def revive(self) -> None:
        print(f"revived")
        # reset variables
        for i in range(len(self.__cooldown)):
            self.__cooldown[i] = 0

        self.position = Vec2.from_cartesian(self.__spawn.x, self.__spawn.y)
        self.velocity = Vec2()
        self.hp = self.max_hp
        self.update(delta=0)

        # re-ad to groups
        self.add(*self.__groups)


class Turret(pg.sprite.Sprite):
    cooldown: float = 0
    accuracy: float = 10  # -1 to 1 / accuracy | in rad
    __character_path: str = "./images/characters/amogus/amogus48left.png"
    __position: Vec2
    __weapon: tp.Type[Bullet]

    def __init__(self, position: Vec2) -> None:
        super().__init__()
        self.__position = position
        self.__weapon = AK47

        self.image = pg.image.load(self.__character_path)
        self.rect = pg.Rect(self.__position.x, self.__position.y, 48, 48)

        self.add(Updated)

    def get_nearest_player(self) -> Player | None:
        closest_distance: float = np.inf
        closest_player: Player | None = None
        for player in Players.sprites():
            player: Player
            dist = abs((self.__position - player.position).length)
            if dist < closest_distance:
                closest_player = player
                closest_distance = dist

        return closest_player

    def update(self, delta: float) -> None:
        self.cooldown = self.cooldown - delta / config.const.T_MULT if self.cooldown > 0 else 0

        target = self.get_nearest_player()
        if target:
            delta = target.position - self.__position
            if delta.length < 1000:
                self.shoot(delta)

    def shoot(self, direction: Vec2) -> None:
        """
        shoot a bulletin the direction of the vector
        """
        # bullet spawner
        if not self.cooldown:
            rand_mod = (randint(0, 2000) - 100) / (1000 * self.accuracy)
            direction.angle += rand_mod
            pos = self.__position + Vec2.from_cartesian(x=0, y=-100)
            b = self.__weapon(
                position=pos,
                direction=direction,
                parent=self,
            )
            self.cooldown += b.cooldown / 4


# GUI stuff
class Scope(pg.sprite.Sprite):
    character_path: str = "./images/weapons/scope.png"
    image: pg.Surface
    position: Vec2
    rect: pg.Rect
    size: int

    def __init__(self):
        super().__init__()

        self.position = Vec2()
        img = pg.image.load(self.character_path)
        self.size = 16

        img = pg.transform.scale(img, (self.size, self.size))
        self.image = img

        self.rect = pg.Rect(self.position.x, self.position.y, self.size, self.size)

        self.add(Updated, FollowsMouse)

    def update(self, _delta: float) -> None:
        self.rect = pg.Rect(self.position.x, self.position.y-self.size*2, self.size, self.size)


class WeaponIndicator(pg.sprite.Sprite):
    character_path: str = "./images/weapons/WEAPON.png"
    scale: tuple[int, int]
    images: pg.surface
    position: Vec2
    rect: pg.Rect
    __weapon: tp.Type[Bullet]

    def __init__(self, position: Vec2, weapon: tp.Type[Bullet]) -> None:
        super().__init__()

        self.position = position
        self.__weapon = weapon
        self.scale: tuple[int, int] = (80, 40)

        img = pg.image.load(self.character_path.replace("WEAPON", self.__weapon.__name__.lower()))
        self.image = pg.transform.scale(img, self.scale)

        self.rect = pg.Rect(self.position.x, self.position.y, *self.scale)

        self.add(Updated)

    @property
    def weapon(self) -> tp.Type[Bullet]:
        return self.__weapon

    @weapon.setter
    def weapon(self, weapon: tp.Type[Bullet]) -> None:
        self.__weapon = weapon
        img = pg.image.load(self.character_path.replace("WEAPON", self.__weapon.__name__.lower()))
        self.image = pg.transform.scale(img, self.scale)