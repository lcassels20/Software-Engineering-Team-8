
# Testingg Project

This guide will walk you through installing the necessary software, configuring PostgreSQL, and running the project.

## Requirements
- A Debian-based virtual machine (e.g., Ubuntu or Debian)
- Sudo privileges

## Installation and Setup

### 1. Install Required Software

**Install Git:**

--sudo apt-get install git
2. Clone the Repository
Clone the Repository and Change into the Directory:
git clone https://github.com/AshtonDavis2003/testingg.git
cd testingg

3. Install Python Tkinter (for GUI support)
sudo apt-get install python3-tk

4. Install pip for Python3
sudo apt-get install python3-pip

5. Install Python Dependencies
Install pg8000:
pip3 install pg8000
Install Pillow:
python3 -m pip install Pillow

6. Install PostgreSQL and Extras
sudo apt-get install postgresql postgresql-contrib

7. Configure PostgreSQL
Change the Password for the postgres User:
Open the PostgreSQL prompt:
sudo -u postgres psql
At the postgres=# prompt, run:
ALTER USER postgres WITH PASSWORD 'student';
Exit the prompt:
\q

8. Run the Code
python3 main.py
If all steps are followed correctly, the application should run without PostgreSQL authentication errors.

Game Instructions
Play the Game: Click the Play button.
Add a Player: Click Add Player on the respective team.
Submit Players: After entering players, click Submit Players for each team to send it to the player action.
Start Game: Click Start Game to begin playing.
Other Options:
Users can change the network or clear teams if needed.
Press Esc on your keyboard to exit full-screen mode.
Click the X in the popup window to end the game.
Debugging: The terminal will display all UDP transmission handling.
Copy

