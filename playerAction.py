import tkinter as tk
from database import get_connection

def fetch_players():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    # Select player_id, name, equipment_id, and team.
    cursor.execute("SELECT player_id, name, equipment_id, team FROM players ORDER BY id")
    players = cursor.fetchall()
    cursor.close()
    conn.close()
    return players

def create_scrollable_frame(parent, height):
    """Creates and returns a scrollable frame inside the given parent with a fixed height."""
    canvas = tk.Canvas(parent, bg=parent["bg"], highlightthickness=0, height=height)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=parent["bg"])
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return scroll_frame

def start_game(root, players=None):
    global player_scores

    # Clear all widgets from the current window.
    for widget in root.winfo_children():
        widget.destroy()
    
    # Use the passed players list if provided.
    if players is None:
        players = fetch_players()
    
    # Separate players based on the team value.
    red_team = [player for player in players if player[3] == "Red"]
    green_team = [player for player in players if player[3] == "Green"]
    
    # Configure grid: row 0 for team frames, row 1 for the bottom timer area.
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    
    # Create frames for Red and Green teams with yellow borders.
    red_frame = tk.Frame(root, bg="#592020", highlightthickness=2, highlightbackground="#FFFF33")
    red_frame.grid(row=0, column=0, sticky="nsew")
    green_frame = tk.Frame(root, bg="#20592e", highlightthickness=2, highlightbackground="#FFFF33")
    green_frame.grid(row=0, column=1, sticky="nsew")
    
    # --- Red Team Layout ---
    red_score_label = tk.Label(red_frame, text="Score: 0", bg="#592020", fg="#FFFF33", font=("Arial", 16))
    red_score_label.pack(pady=5)
    
    red_logo = tk.PhotoImage(file="redTeam.png")
    red_title = tk.Label(red_frame, image=red_logo, bg="#592020")
    red_title.image = red_logo
    red_title.pack(pady=10)
    
    # Scrollable player list.
    red_players_frame = create_scrollable_frame(red_frame, height=250)
    red_players_frame.configure(bg="#592020")
    if red_team:
        for player in red_team:
            text = f"ID: {player[0]} | Name: {player[1]} | Equipment: {player[2]}"
            label = tk.Label(red_players_frame, text=text, bg="#592020", fg="#FFFF33", font=("Arial", 12))
            label.pack(anchor="w", pady=2)
    else:
        tk.Label(red_players_frame, text="No players found", bg="#592020", fg="#FFFF33", font=("Arial", 12)).pack(pady=10)
    
    # Latest Action section immediately under player names.
    tk.Label(red_frame, text="Latest Action:", bg="#592020", fg="#FFFF33", font=("Arial", 14, "bold")).pack(pady=(10,0))
    red_latest_action = tk.Label(red_frame, text="", bg="#592020", fg="#FFFF33", font=("Arial", 12))
    red_latest_action.pack(pady=(0,10))
    
    # --- Green Team Layout ---
    green_score_label = tk.Label(green_frame, text="Score: 0", bg="#20592e", fg="#FFFF33", font=("Arial", 16))
    green_score_label.pack(pady=5)
    
    green_logo = tk.PhotoImage(file="greenTeam.png")
    green_title = tk.Label(green_frame, image=green_logo, bg="#20592e")
    green_title.image = green_logo
    green_title.pack(pady=10)
    
    green_players_frame = create_scrollable_frame(green_frame, height=250)
    green_players_frame.configure(bg="#20592e")
    if green_team:
        for player in green_team:
            text = f"ID: {player[0]} | Name: {player[1]} | Equipment: {player[2]}"
            label = tk.Label(green_players_frame, text=text, bg="#20592e", fg="#FFFF33", font=("Arial", 12))
            label.pack(anchor="w", pady=2)
    else:
        tk.Label(green_players_frame, text="No players found", bg="#20592e", fg="#FFFF33", font=("Arial", 12)).pack(pady=10)
    
    tk.Label(green_frame, text="Latest Action:", bg="#20592e", fg="#FFFF33", font=("Arial", 14, "bold")).pack(pady=(10,0))
    green_latest_action = tk.Label(green_frame, text="", bg="#20592e", fg="#FFFF33", font=("Arial", 12))
    green_latest_action.pack(pady=(0,10))
    
    # --- Bottom Timer Area ---
    bottom_frame = tk.Frame(root, bg="#AB7E02")
    bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
    timer_label = tk.Label(bottom_frame, text="", font=("Arial", 24), fg="black", bg="#AB7E02")
    timer_label.pack(pady=10)
    
    # Handle base hits 
def handle_score_event(player_id, team, score_label, players_frame):
    """
    Handles scoring events by updating the player's score and codename.
    """
    if player_id not in player_scores:
        print(f"Player ID {player_id} not found.")
        return

    # Update the player's score
    player_scores[player_id]["score"] += 100

    # Add a stylized "B" to the codename if not already present
    if not player_scores[player_id]["codename"].startswith("B "):
        player_scores[player_id]["codename"] = f"B {player_scores[player_id]['codename']}"

    # Update the score label
    total_score = sum(player["score"] for player in player_scores.values() if player["team"] == team)
    score_label.config(text=f"Score: {total_score}")

    # Update the player list in the UI
    for widget in players_frame.winfo_children():
        widget.destroy()
    for player_id, player_data in player_scores.items():
        if player_data["team"] == team:
            text = f"ID: {player_id} | Name: {player_data['codename']} | Score: {player_data['score']}"
            label = tk.Label(players_frame, text=text, bg=players_frame["bg"], fg="#FFFF33", font=("Arial", 12))
            label.pack(anchor="w", pady=2)
    
    
    # Timer countdown function.
    def update_timer(seconds):
        if seconds > 0:
            mins, secs = divmod(seconds, 60)
            timer_label.config(text=f"{mins:02d}:{secs:02d}")
            # Print update to terminal only every 10 seconds.
            if seconds % 10 == 0:
                print(f"Timer update: {mins:02d}:{secs:02d}")
            root.after(1000, update_timer, seconds-1)
        else:
            timer_label.config(text="Game is starting")
            print("Game is starting")
    
    # Initially output "Game is starting" for 2 seconds, then start countdown.
    timer_label.config(text="Game is starting")
    print("Game is starting")
    root.after(2000, lambda: update_timer(360)) #Needs to be 360 seconds to run for 6 minutes

    # Play one of the 8 music tracks at random each game.
    music = randomMusic()
    music.play()
    
    # ========== UDP/TRAFFIC GENERATOR INTEGRATION ==========
    # Send the '202' signal to the traffic generator to begin sending messages
    import socket
    import config
    signal_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    signal_sock.sendto(b"202", (config.NETWORK_ADDRESS, 7500))
    print("Sent '202' to traffic generator")

    # Start the UDP server in the background to listen for events from the generator
    import udpServer
    import threading
    score_labels = {"Red": red_score_label, "Green": green_score_label}
    player_frames = {"Red": red_players_frame, "Green": green_players_frame}
    threading.Thread(
        target=udpServer.run_server,
        args=(score_labels, player_frames),
        daemon=True

    

# For testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Player Actions")
    root.geometry("800x600")
    start_game(root)
    root.mainloop()
