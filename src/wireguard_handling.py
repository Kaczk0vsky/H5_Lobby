import os
import subprocess
import time

from src.settings_reader import load_wireguard_settings


class WireguardClient:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.wireguard_path = load_wireguard_settings()["wireguard_path"]

    def set_wireguard_state(self, state: bool):
        config_file = os.path.join(os.getcwd(), f"{self.user_name}.conf")

        try:
            if state:
                subprocess.run(
                    f'"{self.wireguard_path}" /installtunnelservice "{config_file}"',
                    check=True,
                    capture_output=True,
                    text=True,
                    shell=True,
                )
            else:
                subprocess.run(
                    f'sc stop "WireGuardTunnel${self.user_name}"',
                )

        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)

    @staticmethod
    def generate_keys():
        """Generate a WireGuard private and public key pair."""
        private_key = subprocess.check_output("wg genkey", shell=True).strip().decode()
        public_key = (
            subprocess.check_output(f"echo {private_key} | wg pubkey", shell=True)
            .strip()
            .decode()
        )
        return private_key, public_key

    @staticmethod
    def create_new_client(
        client: str, server_public_key: str, client_private_key: str, client_ip: str
    ):
        config_content = [
            "[Interface]",
            f"PrivateKey = {client_private_key}",
            f"Address = {client_ip}/24",
            "DNS = 8.8.8.8, 1.1.1.1",
            "",
            "[Peer]",
            f"PublicKey = {server_public_key}",
            "Endpoint = 4.231.97.96:51820",
            "AllowedIPs = 10.0.0.0/24",
            "PersistentKeepalive = 25",
        ]

        # Write to client configuration file
        config_path = os.path.join(os.getcwd(), f"{client}.conf")
        with open(config_path, "w") as file:
            file.write("\n".join(config_content))
