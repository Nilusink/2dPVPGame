"""
Author:
Nilusink
"""
from core.constants import *
from core.groups import *
import string
import json
import time
import os


class _Game:
    def __init__(self, world_path: str, window_size: tuple[int, int] = ...):
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

    def on_floor(self, point: Vec2):
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
