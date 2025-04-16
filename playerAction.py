import tkinter as tk
from database import get_connection

player_scores = {}  # Tracks player scores and codenames

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

def handle_score_event(player_id, team, score_label, players_frame):
    if player_id not in player_scores:
        print(f"Player ID {player_id} not found.")
        return

    player_scores[player_id]["score"] += 10

    if player_scores[player_id]["score"] < 0:
        player_scores[player_id]["score"] = 0

    total_score = sum(player["score"] for player in player_scores.values() if player["team"] == team)
    score_label.config(text=f"Score: {total_score}")

    for widget in players_frame.winfo_children():
        widget.destroy()

    sorted_players = sorted(
        [(pid, pdata) for pid, pdata in player_scores.items() if pdata["team"] == team],
        key=lambda x: x[1]["score"], reverse=True)

    for pid, pdata in sorted_players:
        label = tk.Label(players_frame, text=f"ID: {pid} | Name: {pdata['codename']} | Score: {pdata['score']}",
                         bg=players_frame["bg"], fg="#FFFF33", font=("Arial", 12))
        label.pack(anchor="w", pady=2)

def handle_base_hit(player_id, team, score_label, players_frame):
    if player_id not in player_scores:
        print(f"Base hit ignored — player {player_id} not found.")
        return

    # Award 100 points and tag with "B " if not already
    player_scores[player_id]["score"] += 100
    if not player_scores[player_id]["codename"].startswith("B "):
        player_scores[player_id]["codename"] = f"B {player_scores[player_id]['codename']}"

    total_score = sum(player["score"] for player in player_scores.values() if player["team"] == team)
    score_label.config(text=f"Score: {total_score}")

    for widget in players_frame.winfo_children():
        widget.destroy()

    sorted_players = sorted(
        [(pid, pdata) for pid, pdata in player_scores.items() if pdata["team"] == team],
        key=lambda x: x[1]["score"], reverse=True)

    for pid, pdata in sorted_players:
        label = tk.Label(players_frame, text=f"ID: {pid} | Name: {pdata['codename']} | Score: {pdata['score']}",
                         bg=players_frame["bg"], fg="#FFFF33", font=("Arial", 12))
        label.pack(anchor="w", pady=2)

def launch_game_screen():
    import tkinter as tk
    import threading
    import GUI
    import randomMusic

    root = tk.Toplevel()
    root.title("Photon Gameplay")
    root.geometry("1000x600")
    root.configure(bg="black")

    frame = tk.Frame(root, bg="black")
    frame.pack(fill="both", expand=True)

    score_labels = {"Red": None, "Green": None}
    player_frames = {"Red": None, "Green": None}

    # RED TEAM FRAME
    red_frame = tk.Frame(frame, bg="darkred")
    red_frame.pack(side="left", fill="both", expand=True)

    tk.Label(red_frame, text="RED TEAM", bg="darkred", fg="white", font=("Arial", 18)).pack(pady=10)
    score_labels["Red"] = tk.Label(red_frame, text="Score: 0", bg="darkred", fg="yellow", font=("Arial", 16))
    score_labels["Red"].pack(pady=5)
    player_frames["Red"] = tk.Frame(red_frame, bg="darkred")
    player_frames["Red"].pack(pady=10)

    # GREEN TEAM FRAME
    green_frame = tk.Frame(frame, bg="darkgreen")
    green_frame.pack(side="right", fill="both", expand=True)

    tk.Label(green_frame, text="GREEN TEAM", bg="darkgreen", fg="white", font=("Arial", 18)).pack(pady=10)
    score_labels["Green"] = tk.Label(green_frame, text="Score: 0", bg="darkgreen", fg="yellow", font=("Arial", 16))
    score_labels["Green"].pack(pady=5)
    player_frames["Green"] = tk.Frame(green_frame, bg="darkgreen")
    player_frames["Green"].pack(pady=10)

    # CENTER PLAY-BY-PLAY + RETURN BUTTON
    center_frame = tk.Frame(frame, bg="black")
    center_frame.pack(side="left", fill="both", expand=True)

    log_label = tk.Label(center_frame, text="Play-by-Play", bg="black", fg="white", font=("Arial", 16))
    log_label.pack()

    log_box = tk.Text(center_frame, bg="black", fg="#00FF00", height=20, wrap="word")
    log_box.pack(fill="both", expand=True, padx=10)

    scrollbar = tk.Scrollbar(log_box)
    scrollbar.pack(side="right", fill="y")
    log_box.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=log_box.yview)

    def update_log(msg):
        log_box.insert("end", f"{msg}\n")
        log_box.see("end")

    def back_to_entry():
        root.destroy()
        GUI.teamRegistration()

    tk.Button(center_frame, text="Return to Player Entry", command=back_to_entry, bg="#FFFF33", fg="black").pack(pady=10)

    import udpServer
    threading.Thread(target=udpServer.run_server, args=(score_labels, player_frames), daemon=True).start()

    def flash_high_team():
        while True:
            try:
                r_score = int(score_labels["Red"].cget("text").split(":")[1])
                g_score = int(score_labels["Green"].cget("text").split(":")[1])
                if r_score > g_score:
                    score_labels["Red"].config(fg="red" if score_labels["Red"].cget("fg") != "red" else "yellow")
                elif g_score > r_score:
                    score_labels["Green"].config(fg="green" if score_labels["Green"].cget("fg") != "green" else "yellow")
                root.after(1500)
            except Exception:
                break

    threading.Thread(target=flash_high_team, daemon=True).start()
    threading.Thread(target=randomMusic.play, daemon=True).start()

    root.mainloop()

def send_game_end_signal():
    import udpSocket
    for _ in range(3):
        udpSocket.transmit_equipment_code("221")




