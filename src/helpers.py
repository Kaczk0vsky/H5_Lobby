import ctypes
import pygame
import os
import ssl
import smtplib

from email.message import EmailMessage


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


def send_email(userdata: dict):
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
