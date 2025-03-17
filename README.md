# Software-Engineering-Team-8
Group project for the software engineering class of Spring 2024.

## Members:
| Real Names | Github Usernames|
| ------------- | ------------- |
| Mylia Rosen  | mcr61  |
| Lauren Cassels  | lcassels20 |
| Christian Conway | Christian-Conway |
| Ashton Davis | AshtonDavis2003 |
| McKayla Lemon |   McKaylaLemon  |


This guide will walk you through installing the necessary software, configuring PostgreSQL, and running the project.

Requirements
A Debian-based virtual machine (e.g., Ubuntu or Debian)
Sudo privileges

Installation and Setup:

1. Install Required Software
Install Git
sudo apt-get install git


2. Clone the Repository and load it
git clone https://github.com/AshtonDavis2003/testingg.git
Change into the Repository Directory
cd testingg

3. Install Python Tkinter (for GUI support)
sudo apt-get install python3-tk

4. Install pip for Python3
sudo apt-get install python3-pip
Install Python Dependencies

5. Install pg8000:
pip3 install pg8000

6. Install Pillow:
python3 -m pip install Pillow

7.Install PostgreSQL and Extras
sudo apt-get install postgresql postgresql-contrib

8. Configure PostgreSQL
Change the Password for the postgres User
Open the PostgreSQL prompt:
sudo -u postgres psql
At the postgres=# prompt, run:
ALTER USER postgres WITH PASSWORD 'student';
Exit the prompt:
\q


9. Run the Code
With everything installed and configured, start the application:
python3 main.py
If all steps are followed correctly, the application should run without PostgreSQL authentication errors.

game instructions:
to play the game click play.
to enter a player click add player on the respective team.
after a team is entered click submit players for each team to send it to the playeraction.
Now click start game to play the game.
users are allowed to chnage the network or clear teams if they wanted.
click esc on your keyboard if you do not want full screen.
click on the x in the popup window to end the game.
the terminal will show all handling of the upd transmuission.
