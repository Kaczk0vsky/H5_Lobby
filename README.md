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

##### 5. Setup RabitMQ broker
1) `sudo apt update && sudo apt install rabbitmq-server -y`
2) `sudo systemctl status rabbitmq-server`
3) `sudo systemctl start rabbitmq-server`
4) `sudo systemctl enable rabbitmq-server`
5) `sudo rabbitmqctl add_user myuser mypassword` - myuser and mypassword is to be set by you
6) `sudo rabbitmqctl set_user_tags myuser administrator` - same here
7) `sudo rabbitmqctl set_permissions -p / myuser ".*" ".*" ".*"` - same here

##### 6. Create django service file
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
3) `sudo systemctl daemon-reload`
4) `sudo systemctl enable django`
5) `sudo systemctl start django`
6) `sudo systemctl status django`

##### 7. Create celery service file
1) `sudo nano /etc/systemd/system/celery.service`
2) paste into the file:
```
[Unit]
Description=Celery Worker
After=network.target rabbitmq-server.service

[Service]
Type=forking
User=h5lobby
Group=h5lobby
WorkingDirectory=/home/h5lobby/H5_Lobby
Environment="PATH=/home/h5lobby/H5_Lobby/venv/bin"
ExecStart=/home/h5lobby/H5_Lobby/venv/bin/celery -A admin_settings worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
3) `sudo systemctl daemon-reload`
4) `sudo systemctl enable celery`
5) `sudo systemctl start celery`
6) `sudo systemctl status celery`

##### 8. SoftEtherVPN server creation
1) `sudo apt-get install lynx -y`
2) `lynx http://www.softether-download.com/files/softether/` - find latets version, select linux, then VPN server. Next press "d" to download the file.
3) `tar -xvzf softether-vpnserver-v4.42-9798-rtm-2023.06.30-linux-x64-64bit.tar.gz ` - the file name may be different, change accordingly
4) `cd vpnserver/ & make`
5) `sudo mv vpnserver /usr/local/`
6) `cd  /usr/local/vpnserver/`
7) `chmod 600 * & chmod 700 vpnserver & chmod 700 vpncmd`
8) `sudo nano /etc/init.d/vpnserver` - and paste into the file:
```
#!/bin/sh
### BEGIN INIT INFO
# Provides: vpnserver
# Required-Start:
# Required-Stop:
# Default-Start: 2 3 4 5
# Default-Stop:
# Short-Description: SoftEtherVPNServer
### END INIT INFO

DAEMON=/usr/local/vpnserver/vpnserver
LOCK=/var/lock/subsys/vpnserver
test -x $DAEMON || exit 0
case "$1" in
start)
$DAEMON start
touch $LOCK
;;
stop)
$DAEMON stop
rm $LOCK
;;
restart)
$DAEMON stop
sleep 3
$DAEMON start
;;
*)
echo "Usage: $0 {start|stop|restart}"
exit 1
esac
exit 0
```
9) `sudo chmod 755 /etc/init.d/vpnserver`
10) `sudo nano /etc/systemd/system/vpnserver.service` - and paste into the file:
```
[Unit]
Description=SoftEther VPN Server
After=network.target

[Service]
ExecStart=/usr/local/vpnserver/vpnserver start
ExecStop=/usr/local/vpnserver/vpnserver stop
Restart=always
User=root
Group=root
Type=forking

[Install]
WantedBy=multi-user.target
```
11) `sudo chmod +x /usr/local/vpnserver/vpnserver`
12) `sudo systemctl daemon-reload`
13) `sudo systemctl enable vpnserver.service`
14) `sudo systemctl restart vpnserver`
15) `sudo update-rc.d vpnserver defaults`
16) `sudo chmod +x /usr/local/vpnserver/vpncmd`
17) `sudo /usr/local/vpnserver/vpncmd` - press option 1 and then ENTER twice
18) `ServerPasswordSet` - set password
19) `HubCreate VPN` - set password, where VPN is the name of the Hub
20) `Hub VPN`
21) `SecureNatEnable`
22) `UserCreate <name>` - create user with <name>
23) `UserPasswordSet <name>` - set password for <name>
24) `IPsecEnable` - click yes, no, yes, then set the key, and then paste the HUB name (VPN in this case)
25) `exit` - to exit the VPN configuration
26) `sudo ufw allow 443/tcp`
27) paste below commands:
```
sudo ufw allow 443/tcp
sudo ufw allow 5555/tcp
sudo ufw allow 992/tcp
sudo ufw allow 1194/udp
sudo ufw allow 22/tcp
```
28) `sudo systemctl restart vpnserver-service`

##### 9. (OPTIONAL - for cloud solutions) Set inbound rules for Ports
Only needed if you use some clound hostef Virtual Machine. Open all ports that were described before.
