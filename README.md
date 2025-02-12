# H5 Lobby Client and Server
![H5 Lobby Logo](https://raw.githubusercontent.com/Kaczk0vsky/H5_Lobby/main/resources/logo.png)
There are two versions that will be covered in this file. First one will be installation for a developer from the player side aswell as covering the most important features. The second one will be installation and full setup guide for the server on Linux machine.
##Player side
This is simply what the player will see after downloading the installator and running the .exe file.
###Key features
- logging into the game and starting the game search through **Find game** button,
- after finding the game showing the window with opponnent found and options to **Accept** or **Decline** this matchup,
- after accepting launching the game .exe file for both players that agreed to play,
- after declining removing the player from the queue, while leaving the other one in queue,
- **Registration** option for the new players,
- after registration creating VPN connection and adding player to the ranked system, that collects points for winning the games and callculates the overall points gains and loses,
- **Forgot password** option,
- set of security measures that do not allow any unwanted operation.
- **Options** button for changing the resolution and in the future also other things,

###Installation guide
1. Clone the repository.
2. Install poetry:
`pip3 install poetry`
3. Check if poetry is installed:
`poetry --version`
4. Install the packages:
`poetry install`
5. Run the program:
`poetry run python main.py`

##Instalation from Server side (Linux machine)
Will be covered later...