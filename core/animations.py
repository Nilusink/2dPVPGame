from core.new_types import Vec2
import pygame as pg
import os


def play_animation(directory: str, position: Vec2, delay: float = .2) -> None:
    """
    play an animation from a directory
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"No such file or directory: {directory}")

    images = os.listdir(directory)
    for image in images:
        img = pg.image.load(directory+"/"+image)
