import subprocess
import os

SOURCE_FILE = "main.py"
OBFUSCATED_DIR = "obfuscated"
BUILD_DIR = "build"
EXE_NAME = "H5_Lobby"
SOURCE_PATH_SRC = os.path.join(os.getcwd(), "src/")
DEST_PATH_SRC = "src"
SOURCE_PATH_WIDGETS = os.path.join(os.getcwd(), "widgets/")
DEST_PATH_WIDGETS = "widgets"
SOURCE_PATH_SETTINGS = os.path.join(os.getcwd(), "settings.toml")
DEST_PATH_SETTINGS = "settings.toml"


def run_command(command):
    process = subprocess.run(command, shell=True, check=True)
    if process.returncode != 0:
        print(f"Error during - {command}")
        exit(1)


def create_exe_file():
    # Run PyArmor to obfuscate all the needed files
    # run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_PATH_SRC}")
    # run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_PATH_WIDGETS}")
    # run_command(f"pyarmor gen -O {OBFUSCATED_DIR} {SOURCE_FILE}")

    # Run pyinstaller to create an .exe file
    run_command(
        f'pyinstaller --onefile --clean \
            --icon=resources/icon.ico \
            --version-file=version.txt \
            --add-data="src:{DEST_PATH_SRC}" \
            --add-data="widgets:{DEST_PATH_WIDGETS}" \
            --hidden-import=pygame \
            --collect-submodules=pygame \
            --hidden-import=toml \
            --collect-submodules=toml \
            --hidden-import=django \
            --collect-submodules=django \
            --hidden-import=requests \
            --collect-submodules=requests \
            --hidden-import=dotenv \
            --collect-submodules=dotenv \
            --hidden-import=pygetwindow \
            --collect-submodules=pygetwindow \
            --hidden-import=psutil \
            --collect-submodules=psutil \
            --hidden-import=dotenv \
            --collect-submodules=dotenv \
            --hidden-import=tkinter \
            --collect-submodules=tkinter \
            --hidden-import=_tkinter \
            --collect-submodules=_tkinter \
            --hidden-import=easygui \
            --collect-submodules=easygui \
            --hidden-import=pygetwindow \
            --collect-submodules=pygetwindow \
            --hidden-import=psycopg2 \
            --collect-submodules=psycopg2 \
            --hidden-import=psutil \
            --collect-submodules=psutil \
            --hidden-import=keyboard \
            --collect-submodules=keyboard \
            --hidden-import=logging \
            --collect-submodules=logging \
            --name={EXE_NAME} main.py'
    )

    # Remove the obfuscated directory
    # run_command(f"rmdir /S /Q {OBFUSCATED_DIR}")

    # Remove spec file
    os.remove(os.path.join(os.getcwd(), f"{EXE_NAME}.spec"))

    run_command(f"rmdir /S /Q {BUILD_DIR}")


if __name__ == "__main__":
    create_exe_file()
