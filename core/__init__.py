"""
Author:
Nilusink
"""
from core.animations import play_animation
from threading import Timer

from core.basegame import Game
from core.constants import *
from core.groups import *


class Bullet(pg.sprite.Sprite):
    cooldown: float = 0
    speed: float = 0
    _size: int = 0
    parent: pg.sprite.Sprite
    character_path: str
    last_angle: float
    velocity: Vec2
    damage: float
    rect: pg.Rect
    __original_image: pg.Surface
    __position: Vec2

    def __init__(self, position: Vec2, direction: Vec2, parent: pg.sprite.Sprite, initial_velocity: Vec2 = Vec2()):
        super().__init__()
        self.__position = position
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
        self.__original_image = img
        self.image = pg.transform.rotate(self.__original_image, -self.velocity.angle * (180/PI))
        self.rect = pg.Rect(self.__position.x, self.__position.y, self._size, self._size)

        self.add(Updated, CollisionDestroyed, FrictionAffected, GravityAffected, WallBouncer)

    @property
    def position(self) -> Vec2:
        return self.__position

    @property
    def on_ground(self) -> bool:
        return Game.on_floor(self.__position)

    @property
    def out_of_bounds(self) -> bool:
        return all([
            not -200 < self.__position.x < WINDOW_SIZE[0] + 200,
            not -200 < self.__position.y < WINDOW_SIZE[1] + 200,
        ])

    def update(self, delta: float) -> None:
        self.__position += self.velocity * delta

        if self.out_of_bounds or self.on_ground:
            self.on_death()

        self.image = pg.transform.rotate(self.__original_image, -self.velocity.angle * (180/PI))
        self.last_angle = self.velocity.angle

        self.rect = pg.Rect(
            self.__position.x - self._size / 2,
            self.__position.y - self._size / 2,
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
    cooldown = BULLET_COOLDOWN
    damage = BULLET_DAMAGE
    speed = BULLET_SPEED
    _size = 16


class Rocket(Bullet):
    explosion_animation: str = "./images/animations/explosion/"
    character_path: str = "./images/weapons/rocket.png"
    cooldown = ROCKET_COOLDOWN
    damage = ROCKET_DAMAGE
    speed = ROCKET_SPEED
    _size = 64
    hp = 2

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add(WallBouncer)

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
            if sprite is not self:
                sprite.hit(self.damage)

        self.kill()


class Sniper(Bullet):
    character_path: str = "./images/weapons/bullet.png"
    cooldown = SNIPER_COOLDOWN
    damage = SNIPER_DAMAGE
    speed = SNIPER_SPEED
    _size = 32


class Player(pg.sprite.Sprite):
    # public
    hp: float
    name: str
    shoots: bool
    velocity: Vec2
    position: Vec2
    image: pg.Surface
    bullet_offset: Vec2
    parent: pg.sprite.Sprite
    max_speed: float = MAX_SPEED
    jump_speed: float = JUMP_SPEED
    controls: tuple[str, str, str]
    character_path: str = "./images/characters/amogus/amogusSIZEDIRECTION.png"

    # private
    __weapon_indicator: "WeaponIndicator"
    __bullets: list[Bullet] = []
    __available_weapons: list
    __weapon: tp.Type[Bullet]
    __events: list[dict] = []
    __max_hp: float = MAX_HP
    __weapon_index: int = 0
    __cooldown: list[float]
    __facing: str = "right"
    __groups: list | tuple
    __max_hp: float
    __spawn: Vec2
    __size: int = 32

    def __init__(self,
                 spawn_point: Vec2,
                 *groups_,
                 velocity: Vec2 = ...,
                 controls: tuple[str, str, str] = ("", "", ""),
                 shoots: bool = False,
                 name: str = ""
                 ) -> None:

        if velocity is ...:
            velocity = Vec2()

        super().__init__(*groups_)
        # weapon config
        self.__weapon_index: int = 0
        self.__available_weapons: tuple = (
            AK47,
            Sniper,
            Rocket
        )
        self.__weapon: tp.Type[Bullet] = self.__available_weapons[self.__weapon_index]

        # player meta
        self.__spawn = spawn_point
        self.position = Vec2.from_cartesian(spawn_point.x, spawn_point.y)
        self.velocity = velocity
        self.controls = controls
        self.shoots = shoots
        self.name = name

        # player config
        self.hp = self.__max_hp

        self.bullet_offset: Vec2 = Vec2.from_cartesian(
            x=self.size,
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
    def events(self) -> list[dict]:
        tmp = self.__events.copy()
        self.__events.clear()
        return tmp

    @property
    def weapon(self) -> tp.Type[Bullet]:
        return self.__weapon

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
        return Game.on_floor(self.position) and self.velocity.y >= 0

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
        self.rect = pg.Rect(self.position.x, self.position.y - self.size, self.size, self.size)

    def update(self, delta: float) -> None:
        for i, cooldown in enumerate(self.__cooldown):
            self.__cooldown[i] = cooldown - delta / T_MULT if cooldown > 0 else 0

        if self.on_ground:
            if Game.is_pressed(self.controls[0]):
                self.velocity.x = self.max_speed  # if self.velocity.x < self.max_speed else self.max_speed

            if Game.is_pressed(self.controls[1]):
                self.velocity.x = -self.max_speed  # if -self.velocity.x > -self.max_speed else -self.max_speed

            if not Game.is_pressed(self.controls[0]) and not Game.is_pressed(self.controls[1]):
                self.velocity.x = 0

        if Game.is_pressed(self.controls[2]) and self.on_ground:
            self.velocity.y -= self.jump_speed

        if pg.mouse.get_pressed()[0]:
            if not self.cooldown:
                mouse_pos = pg.mouse.get_pos()
                mouse_pos = Vec2.from_cartesian(*mouse_pos)

                direction = mouse_pos - self.position
                self.shoot(direction)

        if Game.is_pressed("scroll_down"):
            self.weapon_index -= 1

        if Game.is_pressed("scroll_up"):
            self.weapon_index += 1

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
            b = self.weapon(
                position=self.position + self.bullet_offset,
                direction=direction,
                parent=self,
                initial_velocity=self.velocity
            )
            self.__bullets.append(b)
            self.cooldown += b.cooldown

            self.__events.append({
                "type": "shot",
                "weapon": self.weapon.__name__,
                "angle": direction.angle
            })

    def hit(self, damage: float) -> None:
        self.hp -= damage
        if self.hp <= 0:
            self.on_death()

    def on_death(self) -> None:
        self.kill()
        Timer(4.20, self.revive).start()

    def revive(self) -> None:
        print(f"revived")
        # reset variables
        self.position = Vec2.from_cartesian(self.__spawn.x, self.__spawn.y)
        self.velocity = Vec2()
        self.hp = self.max_hp
        self.update(delta=0)

        # re-ad to groups
        self.add(*self.__groups)


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
