# H5 Lobby Client and Server
![H5 Lobby Logo](https://raw.githubusercontent.com/Kaczk0vsky/H5_Lobby/main/resources/logo.png?raw=true)

There are two versions that will be covered in this file. First one will be installation for a developer from the player side aswell as covering the most important features. The second one will be installation and full setup guide for the server on Linux machine.
## Player side
This is simply what the player will see after downloading the installator and running the .exe file.
### Key features
- logging into the game and starting the game search through **Find game** button,
- after finding the game showing the window with opponnent found and options to **Accept** or **Decline** this matchup,
- after accepting launching the game .exe file for both players that agreed to play,
- after declining removing the player from the queue, while leaving the other one in queue,
- **Registration** option for the new players,
- after registration creating VPN connection and adding player to the ranked system, that collects points for winning the games and callculates the overall points gains and loses,
- **Forgot password** option,
- set of security measures that do not allow any unwanted operation.
- **Options** button for changing the resolution and in the future also other things,

### Installation guide
1. Clone the repository.
2. Install poetry:
`pip3 install poetry`
3. Check if poetry is installed:
`poetry --version`
4. Install the packages:
`poetry install`
5. Run the program:
`poetry run python main.py`

## Instalation from Server side (Linux machine)
##### 1. Setting Git
1) `sudo apt update && sudo apt install git -y`
2) `git clone https://github.com/Kaczk0vsky/H5_Lobby.git`
3) `cd H5_Lobby`

##### 2. Firewall
1) `sudo ufw allow 8000`
2) `sudo ufw allow 22`
3) `sudo ufw enable`

##### 3. Install Python and create venv
1) `sudo apt update && sudo apt install -y python3 python3-venv python3-pip`
2) `python3 -m venv venv`
3) `source venv/bin/activate`
4) `pip3 install django celery toml`

##### 4. Run django commands
1) `python -m manage makemigrations`
2) `python -m manage migrate`
3) `python -m manage createsuperuser`

##### 5. Create django service file
1) `sudo nano /etc/systemd/system/django.service`
2) paste into the file:
```
[Unit]
Description=Django Application
After=network.target

[Service]
User=h5lobby
Group=h5lobby
WorkingDirectory=/home/h5lobby/H5_Lobby
ExecStart=/home/h5lobby/H5_Lobby/venv/bin/python /home/h5lobby/H5_Lobby/manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
4) `sudo systemctl daemon-reload`
5) `sudo systemctl enable django`
6) `sudo systemctl start django`
7) `sudo systemctl status django`
