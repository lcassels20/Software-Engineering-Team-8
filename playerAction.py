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

def send_game_end_signal():
    import udpSocket
    for _ in range(3):
        udpSocket.transmit_equipment_code("221")

    root.mainloop()

