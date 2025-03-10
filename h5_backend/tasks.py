from celery import shared_task
import subprocess


@shared_task
def add_new_user_to_vpn_server(
    vpn_server_ip: str, vpn_admin_password: str, vpncmd_commands: str
) -> bool:
    vpncmd_path = "/usr/local/vpnserver/vpncmd"
    try:
        command = [
            vpncmd_path,
            vpn_server_ip,
            "/SERVER",
            f"/PASSWORD:{vpn_admin_password}",
            "/CMD",
        ]

        # Debugging logs
        print(f"Executing command: {' '.join(command)}")
        print(f"Commands to execute:\n{vpncmd_commands}")

        result = subprocess.run(
            command, input=vpncmd_commands, text=True, capture_output=True, check=True
        )

        print("VPNCMD Output:", result.stdout)
        if result.returncode != 0:
            print("Error Output:", result.stderr)
            return False

        return True

    except subprocess.CalledProcessError as e:
        print("Subprocess Error:", e.stderr)
        return False
    except Exception as e:
        print("General Error:", str(e))
        return False
