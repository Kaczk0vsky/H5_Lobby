# H5 Lobby - Client/Server
![H5 Lobby Logo](https://raw.githubusercontent.com/Kaczk0vsky/H5_Lobby/main/resources/logo.png?raw=true)

There are three versions different versions of repository installation covered.
- 1) Installation from the player side,
- 2) Installation to ONLY generate .exe launcher file,
- 3) Installation and full setup guide for the server on Linux machine.
For running the Lobby SoftEtherVPN Client is needed.
## Key features
### Login Window

When running H5_Lobby.exe the **Login Window** opens. There are fields to enter nickname and password, checkbox to remember login information and buttons for **Sign In**, **Sign Up** and **Forgot Password?**:
- 1) **Sign In** - check for correctness of inputs, then connects to server and checks if user exists. If everything is fine it opens **Lobby Window**,
- 2) **Sign Up** - window with fields Username, Password, Repeat Password and Email for entering user information. Hover Boxes guide user through registration requirements. After everything is set, we can check with Hover Boxes if requirements were met. If **Submit** is clicked the the request is sent to server and if everything is correct, new user is created. Then the application returns to **Login Window**. **Back** for leaving this view.
- 3) **Forgot Password?** - window with fields Username and Email for entering user information. If erything is correct, request is beeing sent to server. Server responds with sending email with one-time link to change the password. After clicking in the link the password can be changed. If the Username and Email do not match then information is displayed for the user.

Additionally SoftEtherVPN connection is beeing established if not existing. If it is existing the Client simply connects to the Server on Loging in.

### Lobby

Lobby window covers **Find Game**, **Ranking**, **News**, **My Profile**, **Tavern Icon**, **User Icon**, **Settings** and **Quit** buttons and **Players Online**.
- 1) **Find Game** - opens additional window in the middle of the screen. It has a timer for how long player is looking for a game. If match is found then it shows the oponnent nickname, his ranking points, progress bar with time left to accept the game and buttons to accept or cancel:
	- After canceling player is removed from queue and oponnent is thrown back into queue,
	- After time runs out on progress bar player is removed from queue and a message is displayed and oponnent is thrown back into queue,
	- After accepting the player needs to wait for oponnet to accept the game. If oponnent didnt accept the game then player is back in the queue waiting. If both players accepted the game, then the H5_Game.exe opens, Lobby minimalizes and game starts.

When both players are finished they can leave the game. Lobby maximalizes from tray and shows the results. Results window contains infromation about who won, and how much points both player lost/gained.

Every action described here sends a request to the server. Additionally protection from intentional leaving the H5_Game.exe was implemented and wont be cover here. Matchmaking mechanism is working on the server site and wont be covered too.
- 2) **Ranking** - not implemented right now.
- 3) **News** - not implemented right now.
- 4) **My Profile** - opens additional window on the left side (if Settings are opened it closes it and opens in the same place) with curent User statistics (ranking position, ranking points, games played),
- 5) **Tavern Icon** - opens browerser with discord invitation link,
- 6) **User Icon** - not implemented right now.
- 7) **Settings** - opens additional window on the left side (if My Profile is opened it closes it and opens in the same place) with Resolution, Volume, Point Treshold and Toggle Ranked options:
	- a) Resolution - option box, allows user to change window size,
	- b) Volume - slider with value selection from 0 to 100,
	- c) Points Treshold - option box, points from which upwards ranking game oponnent will be searched,
	 d) Toggle Ranked - check box, if checked ranked games will be searched.
- 8) **Quit** - logs out user and quits all processes,
- 9) **Players Online** - list on the right side of the screen with slider. Each box represents player logged in and contains Nickname, Ranking Points and Status of the player. It automatically updates and sorts from the most ranking points to the least.

Whenever a player is diconnected due to his internet connection or server problems the information is beeing displayed about what is happening. Also when its player internet connection the auto reconnecting mechanism was implemented, even when the disconnect happens during playing the game.
### Installation guide
1. Clone the repository.
2. Install poetry:
`pip3 install poetry`
3. Check if poetry is installed:
`poetry --version`
4. Install the packages:
`poetry install`
5. Copy the .env.template and name it .env and then fill the missing variables.
6. Run the program:
`poetry run python main.py`

### Installation guide (only to generate .exe)
1. Clone the repository.
2. Install poetry:
`pip3 install poetry`
3. Check if poetry is installed:
`poetry --version`
4. Install the packages:
`poetry install`
5. Run:
`python -m convert_to_exe.py`
6. File called AshanArena3.exe should be in dist directory
7. Copy the resources and settings.toml to the directory where the AshanArena3.exe is
8. Open the game and enjoy!

## Instalation from Server side (Linux machine)
##### 1. Setting Git
1) `sudo apt update && sudo apt install git -y`
2) `git clone https://github.com/Kaczk0vsky/H5_Lobby.git`
3) `cd H5_Lobby`

##### 2. Firewall
1) `sudo ufw allow 8000`
2) `sudo ufw allow 22`
3) `sudo ufw allow 5000/tcp`
4) `sudo ufw enable`

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

##### 7. Create celery-worker and celery-beat service files
1) `sudo nano /etc/systemd/system/celery-worker.service`
2) paste into the file:
```
[Unit]
Description=Celery Worker
After=network.target rabbitmq-server.service

[Service]
Type=simple
User=h5lobby
Group=h5lobby
WorkingDirectory=/home/h5lobby/H5_Lobby
Environment="PATH=/home/h5lobby/H5_Lobby/venv/bin"
ExecStart=/home/h5lobby/H5_Lobby/venv/bin/celery -A admin_settings worker --loglevel=info -E
Restart=always
RestartSec=5
TimeoutStartSec=600

[Install]
WantedBy=multi-user.target
```
3) `sudo nano /etc/systemd/system/celery-beat.service`
4) paste into the file:
```
[Unit]
Description=Celery Beat Scheduler
After=network.target rabbitmq-server.service

[Service]
Type=simple
User=h5lobby
Group=h5lobby
WorkingDirectory=/home/h5lobby/H5_Lobby
Environment="PATH=/home/h5lobby/H5_Lobby/venv/bin"
ExecStart=/home/h5lobby/H5_Lobby/venv/bin/celery -A admin_settings beat --loglevel=info
Restart=always
RestartSec=5
TimeoutStartSec=600

[Install]
WantedBy=multi-user.target
```
5) `sudo systemctl daemon-reload`
6) `sudo systemctl enable celery-worker.service`
7) `sudo systemctl enable celery-beat.service`
8) `sudo systemctl start celery-worker.service`
9) `sudo systemctl start celery-beat.service`


##### 8. SoftEtherVPN server creation
1) `sudo apt-get install lynx -y & sudo apt install build-essential`
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
29) `sudo ip tuntap add dev tap_vpn mode tap`
30) `sudo ip link set tap_vpn up`
31) In vpncmd - `BridgeCreate VPN /DEVICE:tap_vpn /TAP:yes`
32) `sudo sysctl -w net.ipv4.ip_forward=1`
33) `sudo iptables -t nat -A POSTROUTING -o <interface> -j MASQUERADE`

##### 9. (OPTIONAL - for cloud solutions) Set inbound rules for Ports
Only needed if you use some clound hostef Virtual Machine. Open all ports that were described before.

##### 10. Transfering to HTTPS / Adding Websockets
1) `sudo apt install nginx`
2) `pip install gunicorn & daphne`
3) `sudo nano /etc/systemd/system/django.service`
4) In django.service change ExecStart to: `ExecStart=/home/h5lobby/H5_Lobby/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 admin_settings.wsgi`
5) Create a new file with `sudo nano /etc/nginx/sites-available/django` and put into it: 
```
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/selfsigned.crt; 
    ssl_certificate_key /etc/nginx/selfsigned.key;

    location /static/ {
        alias /home/h5lobby/H5_Lobby/static/;
    }

    location /assets/ {
        root /home/h5lobby/H5_Lobby/frontend/dist;
        index index.html;
        try_files $uri $uri/ =404;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```
6) `sudo ln -s /etc/nginx/sites-available/django /etc/nginx/sites-enabled/`
7) `sudo nano /etc/systemd/system/gunicorn.service` and delete everything and put this code inside:
```
[Unit]
Description=Gunicorn service for H5_Lobby (Django HTTP server)
After=network.target

[Service]
User=h5lobby
Group=www-data
WorkingDirectory=/home/h5lobby/H5_Lobby
ExecStart=/home/h5lobby/H5_Lobby/venv/bin/gunicorn \
  --workers 3 \
  --bind 127.0.0.1:8001 \
  admin_settings.wsgi:application

Restart=always
RestartSec=5
Environment="PATH=/home/h5lobby/H5_Lobby/venv/bin"

[Install]
WantedBy=multi-user.target
```
8) `sudo nano /etc/systemd/system/daphne.service` and delete everything and put this code inside:
```
[Unit]
Description=Daphne ASGI server for H5_Lobby (WebSocket handler)
After=network.target

[Service]
User=h5lobby
Group=www-data
WorkingDirectory=/home/h5lobby/H5_Lobby
ExecStart=/home/h5lobby/H5_Lobby/venv/bin/daphne \
  -b 127.0.0.1 -p 8002 \
  admin_settings.asgi:application

Restart=always
RestartSec=5
Environment="PATH=/home/h5lobby/H5_Lobby/venv/bin"

[Install]
WantedBy=multi-user.target
```
9) `sudo systemctl daemon-reload`
10) `sudo systemctl enable nginx`
11) `sudo systemctl enable gunicorn`
12) `sudo systemctl enable daphne`
13) `sudo systemctl restart nginx`
14) `sudo systemctl restart gunicorn`
15) `sudo systemctl restart daphne`

##### 11. Frontend installation
1) `sudo apt install npm`
2) `npm install`
3) `npm install bootstrap`
4) `cd frontend`
5) `npm run build`
6) `sudo systemctl restart nginx`
7) `sudo systemctl restart django.service`
