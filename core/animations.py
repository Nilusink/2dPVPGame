"""
Author:
Nilusink
"""
from core.basegame import Game
from threading import Thread
import pygame as pg
import time
import os


def play_animation(directory, position, size, surface, delay=.2):
    """
    play an animation from a directory
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"No such file or directory: {directory}")

    position.x -= size.x / 2
    position.y -= size.y / 2

    def inner():
        images = os.listdir(directory)
        print(f"{images=}")
        for image in images:
            img = pg.image.load(directory+"/"+image)
            img = pg.transform.scale(img, (size.x, size.y))
            x = Game.blit(surface, img, position)
            time.sleep(delay)
            Game.unblit(x)

    Thread(target=inner).start()
