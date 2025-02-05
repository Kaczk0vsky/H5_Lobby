import ctypes
import pygame
import os


def delete_objects(object_list: list):
    for object in object_list:
        object.delete_instance()


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def play_on_empty(path: str, volume: float = 1):
    for index in range(0, 8):
        if not pygame.mixer.Channel(index).get_busy():
            pygame.mixer.Channel(index).play(
                pygame.mixer.Sound(os.path.join(os.getcwd(), path)),
                0,
                0,
            )
            pygame.mixer.Channel(index).set_volume(volume)
            return index
