import subprocess
import os

SOURCE_FILE = "main.py"
OBFUSCATED_DIR = "obfuscated"
EXE_NAME = "AshanArena3.exe"
SOURCE_PATH_SRC = os.path.join(os.getcwd(), "src/")
DEST_PATH_SRC = "src"
SOURCE_PATH_WIDGETS = os.path.join(os.getcwd(), "widgets/")
DEST_PATH_WIDGETS = "widgets"
SOURCE_PATH_ADMIN_SETTINGS = os.path.join(os.getcwd(), "admin_settings/")
DEST_PATH_ADMIN_SETTINGS = "admin_settings"
SOURCE_PATH_BACKEND = os.path.join(os.getcwd(), "h5_backend/")
DEST_PATH_BACKEND = "h5_backend"
SOURCE_PATH_SETTINGS = os.path.join(os.getcwd(), "settings.toml")
DEST_PATH_SETTINGS = "settings.toml"


def run_command(command):
    process = subprocess.run(command, shell=True, check=True)
    if process.returncode != 0:
        print(f"Error during - {command}")
        exit(1)


def create_exe_file():
    # Run PyArmor to obfuscate all the needed files
    run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_PATH_SRC}")
    run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_PATH_WIDGETS}")
    run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_PATH_ADMIN_SETTINGS}")
    run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_PATH_BACKEND}")
    run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_FILE}")

    # Run pyinstaller to create an .exe file
    run_command(
        f'pyinstaller --onefile --noconsole \
            --add-data="{OBFUSCATED_DIR}/src:{DEST_PATH_SRC}" \
            --add-data="{OBFUSCATED_DIR}/widgets:{DEST_PATH_WIDGETS}" \
            --add-data="{OBFUSCATED_DIR}/admin_settings:{DEST_PATH_ADMIN_SETTINGS}" \
            --add-data="{OBFUSCATED_DIR}/h5_backend:{DEST_PATH_BACKEND}" \
            --add-data="{OBFUSCATED_DIR}:{DEST_PATH_SETTINGS}" \
            --hidden-import=pygame \
            --collect-submodules=pygame \
            --hidden-import=toml \
            --collect-submodules=toml \
            --hidden-import=django \
            --collect-submodules=django \
            --hidden-import=requests \
            --collect-submodules=requests \
            --hidden-import=easygui \
            --collect-submodules=easygui \
            --hidden-import=dotenv \
            --collect-submodules=dotenv \
            --hidden-import=celery \
            --collect-submodules=celery \
            --name={EXE_NAME} {OBFUSCATED_DIR}/main.py'
    )

    # Remove the obfuscated directory
    run_command(f"rmdir /S /Q {OBFUSCATED_DIR}")


if __name__ == "__main__":
    create_exe_file()
