import os
import subprocess
import time
import psutil
import ctypes

from src.settings_reader import load_vpn_settings
from src.global_vars import env_dict
from utils.logger import get_logger

logger = get_logger(__name__)


class SoftEtherClient:
    """
    A client interface for managing a SoftEther VPN connection.

    This class provides methods to create a VPN client configuration and
    connect or disconnect from the VPN using the SoftEther VPN command-line tool.

    Attributes:
        user_name (str): The username for VPN authentication.
        password (str): The password for VPN authentication.
        vpn_path (str): The path to the SoftEther VPN client directory.
        vpn_cmd_path (str): The full path to the SoftEther VPN command-line executable (vpncmd.exe).
        server_url (str): The SoftEther VPN server address.
        hub_name (str): The name of the VPN hub.

    Methods:
        set_vpn_state(state: bool):
            Connects or disconnects from the VPN based on the provided state.

        create_new_client():
            Creates a new VPN client configuration, including NIC creation,
            account creation, and password setup.
    """

    def __init__(self, user_name: str, password: str):
        self.user_name = user_name
        self.password = password
        self.vpn_path = load_vpn_settings()["vpn_path"]
        self.vpn_cmd_path = os.path.join(self.vpn_path, "vpncmd.exe")
        self.server_url = env_dict["SERVER_URL"]
        self.hub_name = env_dict["VPN_HUB_NAME"]

    def set_vpn_state(self, state: bool):
        if state:
            account_state = "AccountConnect"
        else:
            account_state = "AccountDisconnect"
        command = [
            self.vpn_cmd_path,
            "localhost",
            "/CLIENT",
            "/CMD",
            account_state,
            "H5_Lobby_VPN",
        ]

        soft_ether_state = False
        try:
            for process in psutil.process_iter():
                if process.name() == "vpncmgr_x64.exe":
                    soft_ether_state = True

            if not soft_ether_state:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Please open SoftEther VPN Client!",
                    "Lobby Warning",
                    0,
                )
                subprocess.Popen(
                    f"cd {self.vpn_path} && vpnclient.exe",
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            subprocess.run(command, shell=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.critical("Setting VPN state Error:", e.stderr)

    def create_new_client(self):
        logger.debug("Checking VPN...")
        vpn_server_ip = self.server_url
        vpn_hub = self.hub_name
        vpn_port = "5555"

        # check if adapter already exists
        command = f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD NicList {vpn_hub}'
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Checking existing VPN adapters Error: {e.output}")
            return False

        if "Virtual Network Adapter Name" in result.stdout:
            logger.debug(f"VPN adapter already exists. Skipping...")
        else:
            command = f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD NicCreate VPN'
            try:
                subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                if "Error code: 32" in e.output:
                    pass
                else:
                    logger.warning(f"Creating new VPN adapter Error: {e.output}")
                    return False
            logger.info(f"{vpn_hub} adapter created successfully.")

        # check if account already exists
        command = f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD AccountList {vpn_hub}'
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Checking existing VPN accounts Error: {e.output}")
            return False

        if "VPN Connection Setting Name" in result.stdout:
            logger.debug(f"User account already exists. Skipping...")
            return True
        else:
            commands = [
                f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD AccountCreate H5_Lobby_VPN /SERVER:{vpn_server_ip}:{vpn_port} /HUB:{vpn_hub} /USERNAME:{self.user_name} /NICNAME:{vpn_hub}',
                f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD AccountPasswordSet H5_Lobby_VPN /PASSWORD:{self.password} /TYPE:standard',
            ]
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
                    time.sleep(1)

                except subprocess.CalledProcessError as e:
                    logger.warning(f"Creating new VPN client Error: {e.output}")
                    return False
            logger.info(f"{vpn_hub} account created successfully.")
        return True
