from core.new_types import Vec2
from threading import Thread
import pygame as pg
import time
import os


def play_animation(directory: str, position: Vec2, size: Vec2, surface: pg.Surface, delay: float = .2) -> None:
    """
    play an animation from a directory
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"No such file or directory: {directory}")

    def inner():
        images = os.listdir(directory)
        for image in images:
            img = pg.image.load(directory+"/"+image)
            img = pg.transform.scale(img, (size.x, size.y))
            surface.blit(img, (position.x, position.y))
            time.sleep(delay)

    Thread(target=inner).start()
