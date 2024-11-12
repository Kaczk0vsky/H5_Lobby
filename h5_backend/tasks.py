from celery import shared_task

from h5_backend.settings_handler import save_server_settings

import subprocess


@shared_task
def update_wireguard_config(conf_path, conf_content):
    try:
        with open(conf_path, "a") as file:
            file.write("\n".join(conf_content))
        subprocess.run(
            ["sudo", "systemctl", "restart", "wg-quick@H5_Server.service"],
            check=True,
        )
        print("WireGuard service restarted successfully.")
        save_server_settings()
    except Exception as e:
        print(f"Error in updating WireGuard config: {e}")
        raise e
