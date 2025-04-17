# Software-Engineering-Team-8
Group project for the software engineering class of Spring 2025.
This guide will walk you through installing the necessary software, configuring PostgreSQL, and running the project. 

## Members:
| Real Names | Github Usernames|
| ------------- | ------------- |
| Mylia Rosen  | mcr61  |
| Lauren Cassels  | lcassels20 |
| Christian Conway | Christian-Conway |
| Ashton Davis | AshtonDavis2003 |
| McKayla Lemon |   McKaylaLemon  |


## Requirements
- A Debian-based virtual machine (e.g., Ubuntu or Debian)
- Sudo Privileges

## Installation and Setup
1. **Install Required Software**
  **Install Git**:
   ```sh
   sudo apt-get install git
   ```
2. **Clone the Repository**
  **(Clone and change into the Directory)**:
   ```sh
   git clone git@github.com:lcassels20/Software-Engineering-Team-8.git
   ```
   ```sh
   cd Software-Engineering-Team-8
   ```
3. **Install Python Tkinter (for GUI Support)**:
    ```sh
    sudo apt-get install python3-tk
    ```
4. **Install pip for Python3**:
    ```sh
    sudo apt-get install python3-pip
    ```
5. **Install Python Dependencies**
   **(Install pg8000 and pygame)**:
   ```sh
   pip3 install pg8000
   ```
   ```sh
   pip install pygame
   ```
   **(Install Pillow)**:
   ```sh
   python3 -m pip install Pillow
   ```
6. **Install PostgreSQL and Extras**:
   ```sh
   sudo apt-get install postgresql postgresql-contrib
   ```
7. **Configure PostgreSQL**
   **(Change the Password for the postgres Use)**:
   **(Open the PostgreSQL Prompt)**:
   ```sh
   sudo -u postgres psql
   ```
   **At the Postgres=# prompt, run**:
   ```sh
   ALTER USER postgres WITH PASSWORD 'student';
   ```
   **Exit the prompt**:
   ```sh
   \q
   ```
8. **Create a new terminal instance, then change into the directory**
   ```sh
   cd Software-Engineering-Team-8
   ```
   ```sh
   cd trafficGenerator
   ```
9. **Run this first typing in expected codes in trafficGenerator, then run the game in the other terminal**
10. **Run the Code**
   **(First run database.py before running the main file to clear the table)**
   ```sh
   python3 database.py
   ```
   ```sh
   python3 main.py
   ```
   **If all steps are followed correctly, the application should run without PostgreSQL authentication errors.**

   ## Game Instructions
   **Play the Game**: Click the play button.
   **Add a Player**: Click Add Player on the respective team. Type in identical codes for all players, then start game.
   **Submit Players**: After entering players, click Submit Players for each team to send it to the player action.
   **Start Game**: Click Start Game to begin playing.
   **Other Options**:
       Users can change the network or clear teams if needed.
       Press Esc on your keyboard to exit full-screen mode.
       Click the X in the popup window to end the game.
       Debugging: the terminal will display all UDP transmission handling.










   
   
