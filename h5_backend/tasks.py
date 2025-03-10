from celery import shared_task

import subprocess


@shared_task
def add_new_user_to_vpn_server(
    vpn_server_ip: str, vpn_admin_password: str, vpncmd_commands: str
) -> bool:
    try:
        result = subprocess.run(
            [
                "vpncmd",
                vpn_server_ip,
                "/SERVER",
                "/PASSWORD:",
                vpn_admin_password,
                "/CMD",
            ],
            input=vpncmd_commands,
            text=True,
            capture_output=True,
            shell=True,
            check=True,
        )

        if result.returncode != 0:
            return False
        return True

    except Exception as e:
        return False
