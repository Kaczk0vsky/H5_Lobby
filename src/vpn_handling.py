import os
import subprocess
import time

from src.settings_reader import load_vpn_settings
from src.global_vars import env_dict


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

        try:
            subprocess.run(command, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)

    def create_new_client(self):
        vpn_server_ip = self.server_url
        vpn_hub = self.hub_name
        vpn_port = "443"

        commands = [
            f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD NicCreate VPN',
            f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD AccountCreate H5_Lobby_VPN /SERVER:{vpn_server_ip}:{vpn_port} /HUB:{vpn_hub} /USERNAME:{self.user_name} /NICNAME:VPN',
            f'"{self.vpn_cmd_path}" localhost /CLIENT /CMD AccountPasswordSet H5_Lobby_VPN /PASSWORD:{self.password} /TYPE:standard',
        ]

        for cmd in commands:
            try:
                subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, check=True
                )
                time.sleep(1)

            except subprocess.CalledProcessError as e:
                # TODO: error handling if crashes during one of those commands
                print(f"Error executing command: {cmd}")
                print(e.stderr)
                return False
        return True
