import tkinter as tk
from database import get_connection
import socket
import config
import threading
import udpServer
from randomMusic import play as play_random_music

player_scores = {}

def fetch_players():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, name, equipment_id, team FROM players ORDER BY id")
    players = cursor.fetchall()
    cursor.close()
    conn.close()
    return players

def create_scrollable_frame(parent, height):
    canvas = tk.Canvas(parent, bg=parent["bg"], highlightthickness=0, height=height)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=parent["bg"])
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return scroll_frame

def start_game(root, players=None):
    global player_scores

    for widget in root.winfo_children():
        widget.destroy()

    if players is None:
        players = fetch_players()

    player_scores = {}
    for player in players:
        try:
            equipment_id = int(player[2])
            player_scores[equipment_id] = {
                "codename": player[1],
                "score": 0,
                "team": player[3]
            }
        except:
            continue

    red_team = [player for player in players if player[3] == "Red"]
    green_team = [player for player in players if player[3] == "Green"]

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    red_frame = tk.Frame(root, bg="#592020", highlightthickness=2, highlightbackground="#FFFF33")
    red_frame.grid(row=0, column=0, sticky="nsew")
    green_frame = tk.Frame(root, bg="#20592e", highlightthickness=2, highlightbackground="#FFFF33")
    green_frame.grid(row=0, column=1, sticky="nsew")

    red_score_label = tk.Label(red_frame, text="Score: 0", bg="#592020", fg="#FFFF33", font=("Arial", 16))
    red_score_label.pack(pady=5)

    red_logo = tk.PhotoImage(file="redTeam.png")
    red_title = tk.Label(red_frame, image=red_logo, bg="#592020")
    red_title.image = red_logo
    red_title.pack(pady=10)

    red_players_frame = create_scrollable_frame(red_frame, height=250)
    if red_team:
        for player in red_team:
            text = f"ID: {player[0]} | Name: {player[1]} | Equipment: {player[2]}"
            label = tk.Label(red_players_frame, text=text, bg="#592020", fg="#FFFF33", font=("Arial", 12))
            label.pack(anchor="w", pady=2)

    green_score_label = tk.Label(green_frame, text="Score: 0", bg="#20592e", fg="#FFFF33", font=("Arial", 16))
    green_score_label.pack(pady=5)

    green_logo = tk.PhotoImage(file="greenTeam.png")
    green_title = tk.Label(green_frame, image=green_logo, bg="#20592e")
    green_title.image = green_logo
    green_title.pack(pady=10)

    green_players_frame = create_scrollable_frame(green_frame, height=250)
    if green_team:
        for player in green_team:
            text = f"ID: {player[0]} | Name: {player[1]} | Equipment: {player[2]}"
            label = tk.Label(green_players_frame, text=text, bg="#20592e", fg="#FFFF33", font=("Arial", 12))
            label.pack(anchor="w", pady=2)

    bottom_frame = tk.Frame(root, bg="#AB7E02")
    bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
    bottom_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(1, weight=1)

    # End Game button
    def end_game():
        for _ in range(3):
            signal_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            signal_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            signal_sock.sendto(b"221", (config.NETWORK_ADDRESS, 7500))
        root.destroy()

    end_button = tk.Button(bottom_frame, text="End Game", font=("Arial", 14), bg="#AB7E02", fg="white", command=end_game)
    end_button.grid(row=0, column=0, padx=20, pady=10)

    # Timer label
    timer_label = tk.Label(bottom_frame, text="", font=("Arial", 24), fg="black", bg="#AB7E02")
    timer_label.grid(row=0, column=1, pady=10)

    # Start UDP server
    score_labels = {"Red": red_score_label, "Green": green_score_label}
    player_frames = {"Red": red_players_frame, "Green": green_players_frame}
    threading.Thread(target=udpServer.run_server, args=(score_labels, player_frames), daemon=True).start()

    # Start music
    #threading.Thread(target=play_random_music, daemon=True).start()

    # Send 202 to traffic generator
    signal_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    signal_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    signal_sock.sendto(b"202", (config.NETWORK_ADDRESS, 7500))
    print("Sent '202' to traffic generator")

    def update_timer(seconds):
        if seconds > 0:
            mins, secs = divmod(seconds, 60)
            timer_label.config(text=f"{mins:02d}:{secs:02d}")
            root.after(1000, update_timer, seconds - 1)
        else:
            timer_label.config(text="Game Over")
            print("Game Over")
            for _ in range(3):
                signal_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                signal_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                signal_sock.sendto(b"221", (config.NETWORK_ADDRESS, 7500))

    update_timer(360)

def handle_score_event(player_id, team, score_label, players_frame):
    if player_id not in player_scores:
        print(f"Player ID {player_id} not found.")
        return

    player_scores[player_id]["score"] += 100
    if not player_scores[player_id]["codename"].startswith("B "):
        player_scores[player_id]["codename"] = f"B {player_scores[player_id]['codename']}"

    total_score = sum(player["score"] for player in player_scores.values() if player["team"] == team)
    score_label.config(text=f"Score: {total_score}")

    for widget in players_frame.winfo_children():
        widget.destroy()
    for player_id, player_data in sorted(player_scores.items(), key=lambda x: -x[1]["score"]):
        if player_data["team"] == team:
            text = f"ID: {player_id} | Name: {player_data['codename']} | Score: {player_data['score']}"
            label = tk.Label(players_frame, text=text, bg=players_frame["bg"], fg="#FFFF33", font=("Arial", 12))
            label.pack(anchor="w", pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Player Actions")
    root.geometry("800x600")
    start_game(root)
    root.mainloop()
























































































