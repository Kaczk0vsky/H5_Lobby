import os

from dotenv import load_dotenv

load_dotenv()

bg_sound_volume = 0.2
resolution_choices = [
    "640x480",
    "800x600",
    "1280x720",
    "1600x1200",
    "1920x1080",
    "1920x1440",
    "2560x1440",
    "Fullscreen",
]
transformation_factors = {
    "640x480": (0.3333, 0.4444),
    "800x600": (0.4167, 0.5556),
    "1280x720": (0.6667, 0.6667),
    "1600x1200": (0.8333, 1.1111),
    "1920x1080": (1.0, 1.0),
    "1920x1440": (1.0, 1.3333),
    "2560x1440": (1.3333, 1.3333),
}
fonts_sizes = {
    "640x480": [20, 8],
    "800x600": [24, 12],
    "1280x720": [28, 16],
    "1600x1200": [34, 24],
    "1920x1080": [32, 24],
    "1920x1440": [32, 24],
    "2560x1440": [40, 36],
}
env_dict = {
    "SERVER_URL": os.getenv("SERVER_URL"),
    "SERVER_PORT": int(os.getenv("SERVER_PORT")),
    "SERVER_LISTEN_ON": os.getenv("SERVER_LISTEN_ON"),
    "DJANGO_SECRET_KEY": os.getenv("DJANGO_SECRET_KEY"),
    "RABITMQ_LOGIN": os.getenv("RABITMQ_LOGIN"),
    "RABITMQ_PASSWORD": os.getenv("RABITMQ_PASSWORD"),
    "VPN_SERVER_PASSWORD": os.getenv("VPN_SERVER_PASSWORD"),
    "VPN_HUB_NAME": os.getenv("VPN_HUB_NAME"),
    "VPN_HUB_VPN_PASSWORD": os.getenv("VPN_HUB_VPN_PASSWORD"),
    "VPN_IPSEC_SHARED_KEY": os.getenv("VPN_IPSEC_SHARED_KEY"),
    "PATH_TOKEN": os.getenv("PATH_TOKEN"),
    "PATH_REGISTER": os.getenv("PATH_REGISTER"),
    "PATH_LOGIN": os.getenv("PATH_LOGIN"),
    "PATH_CHANGE_PASSWORD": os.getenv("PATH_CHANGE_PASSWORD"),
    "PATH_PLAYER_OFFLINE": os.getenv("PATH_PLAYER_OFFLINE"),
    "PATH_ADD": os.getenv("PATH_ADD"),
    "PATH_REMOVE": os.getenv("PATH_REMOVE"),
    "PATH_GET_PLAYERS": os.getenv("PATH_GET_PLAYERS"),
    "PATH_CHECK_OPONNENT": os.getenv("PATH_CHECK_OPONNENT"),
}
