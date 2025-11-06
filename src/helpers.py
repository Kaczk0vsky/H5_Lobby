import pygame
import os
import ssl
import smtplib
import time
import re
import socket
import subprocess
import json
import ctypes
import pygetwindow as gw
import asyncio
import threading

from email.message import EmailMessage

from src.global_vars import env_dict
from utils.logger import get_logger

logger = get_logger(__name__)


def delete_objects(object_list: list):
    for object in object_list:
        object.delete_instance()


def play_on_empty_channel(path: str, volume: float = 1) -> int:
    for index in range(0, 8):
        if not pygame.mixer.Channel(index).get_busy():
            pygame.mixer.Channel(index).play(
                pygame.mixer.Sound(os.path.join(os.getcwd(), path)),
                0,
                0,
            )
            pygame.mixer.Channel(index).set_volume(volume)
            return index


def send_email(userdata: dict[str, str], url: str) -> bool:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    EMAIL_SENDER = "ashanarena3@gmail.com"
    EMAIL_PASSWORD = "gllx ckzw degx wjie"

    EMAIL_RECEIVER = userdata["email"]
    SERVER_URL = f"https://{env_dict["SERVER_URL"]}{url}"

    subject = "A Hero’s Quest: Reset Your Password"
    body = f"""\
Greetings {userdata["nickname"]}!

The ancient scrolls whisper that you seek to reclaim access to your account. 
Fear not, for even the mightiest of heroes sometimes misplace their enchanted keys!

To restore your rightful place among the legends, follow this sacred link and forge a new password worthy of your name:

🔗 {SERVER_URL}

But beware! The link shall only remain active for a short while before vanishing into the ether. Should you delay, you must summon the request once more.

May fortune favor you on your journey, and may your armies march ever victorious!

For honor and glory,
AshanArena3 Support
    """

    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host=SMTP_SERVER, port=SMTP_PORT, context=context) as smtp:
        try:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            return True
        except Exception as e:
            return False


def calculate_time_passed(start_time: float) -> tuple[int, int]:
    elapsed_time = round(time.time() - start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    return minutes, seconds


def check_input_correctnes(inputs: list, text_input: dict[any, list]) -> dict[any, list]:
    if "Nickname" in text_input[0][1]:
        nickname = inputs[0].get_string()
        if len(nickname) <= 16 and len(nickname) >= 3:
            text_input[1][0] = True
        else:
            text_input[1][0] = False
        if re.match(r"^[a-zA-Z0-9]+$", nickname):
            text_input[2][0] = True
        else:
            text_input[2][0] = False
    else:
        password = inputs[1].get_string()
        repeat_password = inputs[2].get_string()
        if len(password) >= 8:
            text_input[1][0] = True
        else:
            text_input[1][0] = False
        if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
            text_input[2][0] = True
        else:
            text_input[2][0] = False
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            text_input[3][0] = True
        else:
            text_input[3][0] = False
        if password == repeat_password and text_input[1][0]:
            text_input[4][0] = True
        else:
            text_input[4][0] = False

    return text_input


def get_window() -> gw.Win32Window:
    time.sleep(0.1)
    return gw.getWindowsWithTitle("Tavern of Ashan - Menu")[0]


def check_server_connection(
    host: str = env_dict["SERVER_URL"].replace("https://", "").replace("http://", ""),
    port: int = 443,
    timeout: float = 5.0,
):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def format_state(state: str) -> str:
    return state.replace("_", " ").capitalize()


def get_font(font_size: int = 75) -> pygame.font.Font:
    return pygame.font.Font("resources/Quivira.otf", font_size)


def render_small_caps(text: str, font_size: int, color: tuple) -> pygame.Surface:
    font_large = get_font(font_size)
    font_small = get_font(int(font_size * 0.65))

    surfaces = []
    max_ascent = max(font_large.get_ascent(), font_small.get_ascent())
    max_bottom = 0

    for char in text:
        if char.islower():
            font = font_small
            char_upper = char.upper()
        else:
            font = font_large
            char_upper = char

        surf = font.render(char_upper, True, color)
        ascent = font.get_ascent()
        offset_y = max_ascent - ascent

        bottom = offset_y + surf.get_height()
        max_bottom = max(max_bottom, bottom)

        surfaces.append((surf, offset_y))

    total_width = sum(surf.get_width() for surf, _ in surfaces)
    total_height = max_bottom

    result_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

    x_offset = 0
    for surf, offset_y in surfaces:
        result_surface.blit(surf, (x_offset, offset_y))
        x_offset += surf.get_width()

    return result_surface


def disconnect_unused_network_adapters():
    logger.debug("Checking for unused network adapters to disconnect...")
    try:
        command = ["powershell", "-Command", "Get-NetAdapterStatistics | Select Name, ReceivedBytes, SentBytes | ConvertTo-Json"]
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding="utf-8")
        output = result.stdout.strip()

        if not output:
            logger.debug("No network adapter data returned.")
            return

        adapters = json.loads(output)

        if isinstance(adapters, dict):
            adapters = [adapters]
        elif not isinstance(adapters, list):
            logger.warning("Unexpected data format for network adapters.")
            return

        for adapter in adapters:
            if adapter.get("ReceivedBytes", 1) == 0 and adapter.get("SentBytes", 1) == 0:
                ps_command = f'-Command "Disable-NetAdapter -Name \\"{adapter["Name"]}\\" -Confirm:$false"'
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "powershell.exe", ps_command, None, 1)
                logger.info(f"Disabled unused adapter: {adapter['Name']}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing PowerShell command: {e}")
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON from PowerShell output.")
