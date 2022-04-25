"""
Author:
Nilusink
"""
import string
import json
import time
import os

from constants import *
from groups import *


class _Game:
    def __init__(self, world_path: str, window_size: tuple[int, int] = ...) -> None:
        # initialize pygame
        pg.init()
        pg.font.init()

        if window_size is ...:
            screen_info = pg.display.Info()
            window_size = (screen_info.current_w, screen_info.current_h)

        # create window
        self.screen = pg.display.set_mode(window_size, pg.SCALED)
        self.lowest_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.middle_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.top_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.font = pg.font.SysFont(None, 24)
        pg.display.set_caption("GayGame")
        pg.mouse.set_visible(False)

        # later used variables
        self.__registered_objects: list[pg.sprite.Sprite] = []

        self.__pressed_keys: dict[str, bool] = {}
        self.__last_pressed_keys: dict[str, bool] = {}

        self.__last = time.time()

        self.__platforms: list[dict] = []
        self.__world_config: dict = {}

        self.load_world(world_path)

    def load_world(self, world_path: str) -> None:
        if not os.path.exists(world_path):
            raise FileNotFoundError(f"No such file or directory: {world_path}")

        config: dict = json.load(open(world_path, "r"))
        self.__platforms = config["platforms"]
        config.pop("platforms")
        self.__world_config = config

    def draw_world(self) -> None:
        self.lowest_layer.fill(self.__world_config["background"])
        for platform in self.__platforms:
            pg.draw.rect(self.lowest_layer, platform["color"], pg.Rect(*platform["pos"], *platform["size"]))

    def on_floor(self, point: Vec2) -> bool:
        """
        takes a point and checks if it is on the floor
        """
        for platform in self.__platforms:
            pos = platform["pos"]
            size = platform["size"]
            if all([
                pos[0] < point.x < pos[0] + size[0],
                pos[1] < point.y < pos[1] + size[1]
            ]):
                return True
        return False

    def is_pressed(self, key: str) -> bool:
        return key in self.__pressed_keys and self.__pressed_keys[key]

    def was_last_pressed(self, key: str) -> bool:
        return key in self.__last_pressed_keys and self.__last_pressed_keys[key]

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
        now = time.time()
        delta = now - self.__last

        # for the right feel
        delta *= T_MULT

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
        FollowsMouse.update()

        # calculate stuff
        GravityAffected.calculate_gravity(delta)
        FrictionAffected.calculate_friction(delta)
        WallBouncer.update()

        # update Updated group
        Updated.update(delta)

        # check for collisions
        CollisionDestroyed.update()

        # draw health bars
        HasBars.draw(self.top_layer)

        # draw updated objects and world
        self.draw_world()
        Updated.draw(self.middle_layer)

        # draw layers
        self.screen.blit(self.lowest_layer, (0, 0))
        self.screen.blit(self.middle_layer, (0, 0))
        self.screen.blit(self.top_layer, (0, 0))

        self.__last = now

    @staticmethod
    def end() -> None:
        print(f"quitting...")
        pg.quit()
        exit()


# should be the only instance of the class
Game = _Game("./worlds/world1.json", WINDOW_SIZE)


class Bullet(pg.sprite.Sprite):
    character_path: str

    def __init__(self, position: Vec2, velocity: Vec2, parent: pg.sprite.Sprite) -> None:
        self.__position = position
        self.velocity = velocity
        self.last_angle = 0
        self.parent = parent

        self.cooldown: float
        self.damage: float
        self.speed: float

        self.velocity.length = self.speed

        super().__init__()

        img = pg.image.load(self.character_path)
        img = pg.transform.scale(img, (self._size, self._size))
        self.__original_image = img
        self.image = img
        self.rect = pg.Rect(self.__position.x, self.__position.y, self._size, self._size)

        self.add(Updated, CollisionDestroyed, FrictionAffected, GravityAffected)

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
            self.kill()

        self.image = pg.transform.rotate(self.__original_image, -self.velocity.angle * (180/PI))
        self.last_angle = self.velocity.angle

        self.rect = pg.Rect(
            self.__position.x - self._size / 2,
            self.__position.y - self._size / 2,
            self._size,
            self._size
        )

    def hit(self, _damage: float) -> None:
        self.kill()


class AK47(Bullet):
    character_path: str = "images/weapons/bullet.png"
    cooldown = BULLET_COOLDOWN
    damage = BULLET_DAMAGE
    speed = BULLET_SPEED
    _size = 16


class Rocket(Bullet):
    character_path = str = "images/weapons/rocket.png"
    cooldown = ROCKET_COOLDOWN
    damage = ROCKET_DAMAGE
    speed = ROCKET_SPEED
    _size = 64

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add(WallBouncer)


class Sniper(Bullet):
    character_path: str = "images/weapons/bullet.png"
    cooldown = SNIPER_COOLDOWN
    damage = SNIPER_DAMAGE
    speed = SNIPER_SPEED
    _size = 32


class Player(pg.sprite.Sprite):
    character_path: str = "./images/characters/amogus/amogusSIZEDIRECTION.png"

    def __init__(self,
                 position: Vec2,
                 *groups,
                 velocity: Vec2 = ...,
                 controls: tuple[str, str, str] = ("", "", ""),
                 shoots: bool = False
                 ) -> None:

        if velocity is ...:
            velocity = Vec2()

        super().__init__(*groups)
        # weapon config
        self.__weapon_index: int = 0
        self.__available_weapons: tuple = (
            AK47,
            Sniper,
            Rocket
        )
        self.__weapon: tp.Type[Bullet] = self.__available_weapons[self.__weapon_index]

        # player meta
        self.position = position
        self.velocity = velocity
        self.controls = controls
        self.shoots = shoots

        # player config
        self.max_speed = MAX_SPEED
        self.jump_speed = JUMP_SPEED
        self.__max_hp = MAX_HP
        self.hp = self.__max_hp

        self.__size: int = 32
        self.__facing: str = "right"
        self.__bullets: list[Bullet] = []

        self.bullet_offset: Vec2 = Vec2.from_cartesian(
            x=self.size,
            y=-self.size
        )

        self.parent: pg.sprite.Sprite = self

        self.__cooldown: list[float] = [0] * len(self.available_weapons)

        self.image = pg.image.load(self.character_path
                                   .replace("SIZE", str(self.size))
                                   .replace("DIRECTION", self.facing))

        self.update_rect()

        # add to the player group
        self.add(Players, Updated, GravityAffected, FrictionXAffected, CollisionDestroyed, HasBars)

        self.__weapon_indicator: WeaponIndicator = ...
        if self.shoots:
            self.__weapon_indicator = WeaponIndicator(Vec2.from_cartesian(0, 0), self.weapon)

    @property
    def weapon(self) -> tp.Type[Bullet]:
        return self.__weapon

    @weapon.setter
    def weapon(self, weapon: tp.Type[Bullet]) -> None:
        if self.shoots:
            self.__weapon = weapon
            self.__weapon_indicator.weapon = weapon

    @property
    def available_weapons(self) -> tuple:
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
        self.cooldown = self.cooldown - delta / T_MULT if self.cooldown > 0 else 0

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
            b = self.weapon(position=self.position + self.bullet_offset, velocity=direction, parent=self)
            self.__bullets.append(b)
            self.cooldown += b.cooldown

    def hit(self, damage: float) -> None:
        self.hp -= damage
        if self.hp <= 0:
            self.kill()


class Scope(pg.sprite.Sprite):
    character_path: str = "images/weapons/scope.png"

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
