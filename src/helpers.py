import pygame
import os
import ssl
import smtplib
import time
import re

from email.message import EmailMessage


def delete_objects(object_list: list):
    for object in object_list:
        object.delete_instance()


def play_on_empty(path: str, volume: float = 1) -> int:
    for index in range(0, 8):
        if not pygame.mixer.Channel(index).get_busy():
            pygame.mixer.Channel(index).play(
                pygame.mixer.Sound(os.path.join(os.getcwd(), path)),
                0,
                0,
            )
            pygame.mixer.Channel(index).set_volume(volume)
            return index


def send_email(userdata: dict[str, str]) -> bool:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    EMAIL_SENDER = "ashanarena3@gmail.com"
    EMAIL_PASSWORD = "gllx ckzw degx wjie"

    EMAIL_RECEIVER = userdata["email"]

    subject = "A Hero’s Quest: Reset Your Password"
    body = f"""\
    Greetings {userdata["nickname"]}!

    The ancient scrolls whisper that you seek to reclaim access to your account. 
    Fear not, for even the mightiest of heroes sometimes misplace their enchanted keys!

    To restore your rightful place among the legends, follow this sacred link and forge a new password worthy of your name:

    🔗 [Reset Your Password](#)

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


def check_input_correctnes(
    inputs: list, text_input: dict[any, list]
) -> dict[any, list]:
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
