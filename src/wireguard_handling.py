import os
import subprocess


def generate_keys():
    """Generate a WireGuard private and public key pair."""
    private_key = subprocess.check_output("wg genkey", shell=True).strip().decode()
    public_key = (
        subprocess.check_output(f"echo {private_key} | wg pubkey", shell=True)
        .strip()
        .decode()
    )
    return private_key, public_key


def create_new_client(
    client: str, server_public_key: str, client_private_key: str, client_ip: str
):
    config_content = [
        "[Interface]",
        f"PrivateKey = {client_private_key}",
        f"Address = {client_ip}/24",
        "DNS = 1.1.1.1",
        "",
        "[Peer]",
        f"PublicKey = {server_public_key}",
        "Endpoint = 48.209.34.240:51820",
        "AllowedIPs = 0.0.0.0/0",
        "PersistentKeepalive = 25",
    ]

    # Write to client configuration file
    config_path = os.path.join(os.getcwd(), f"{client}.conf")
    with open(config_path, "w") as file:
        file.write("\n".join(config_content))


if __name__ == "__main__":
    # Run for quick generation of .conf file
    client = input("Nickname: ")
    client_ip = input("Client IP: ")

    priv_key, pub_key = generate_keys()
    create_new_client(
        client=client,
        server_public_key="encrypted",
        client_private_key=priv_key,
        client_ip=client_ip,
    )
