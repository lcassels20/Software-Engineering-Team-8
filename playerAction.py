import tkinter as tk
from database import get_connection
import socket, threading, queue
import config
import udpServer

player_scores = {}

# ---------- helper ---------------------------------------------------------
def fetch_players():
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute(
        "SELECT player_id, name, equipment_id, team FROM players ORDER BY id"
    )
    players = cur.fetchall()
    cur.close(); conn.close()
    return players

def create_scrollable_frame(parent, height):
    canvas = tk.Canvas(parent, bg=parent["bg"], highlightthickness=0, height=height)
    vsb   = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=parent["bg"])

    frame.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)

    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return frame
# ---------------------------------------------------------------------------

def start_game(root, players=None):
    global player_scores
    for w in root.winfo_children():
        w.destroy()

    if players is None:
        players = fetch_players()

    # -----------------------------------------------------------------------
    #  BUILD THE GAME LAYOUT
    # -----------------------------------------------------------------------
    player_scores = {int(p[2]): {"codename": p[1], "score": 0, "team": p[3]}
                     for p in players if str(p[2]).isdigit()}

    red_team   = [p for p in players if p[3] == "Red"]
    green_team = [p for p in players if p[3] == "Green"]

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # -- TEAM PANELS --------------------------------------------------------
    def make_team_panel(parent, bg, logo_file, team_players):
        frame = tk.Frame(parent, bg=bg, highlightthickness=2,
                         highlightbackground="#FFFF33")
        score_lbl = tk.Label(frame, text="Score: 0", bg=bg, fg="#FFFF33",
                             font=("Arial", 16))
        score_lbl.pack(pady=5)

        logo = tk.PhotoImage(file=logo_file)
        tk.Label(frame, image=logo, bg=bg).pack(pady=10)
        frame.logo = logo  # keep ref

        players_fr = create_scrollable_frame(frame, 250)
        for p in team_players:
            tk.Label(players_fr,
                     text=f"ID: {p[0]} | Name: {p[1]} | Equipment: {p[2]}",
                     bg=bg, fg="#FFFF33", font=("Arial", 12)
                     ).pack(anchor="w", pady=2)
        return frame, score_lbl, players_fr

    red_fr , red_score , red_players  = make_team_panel(root, "#592020",
                                                        "redTeam.png",  red_team)
    green_fr, green_score, green_players = make_team_panel(root, "#20592e",
                                                           "greenTeam.png", green_team)
    red_fr.grid(row=0, column=0, sticky="nsew")
    green_fr.grid(row=0, column=1, sticky="nsew")

    # -- BOTTOM BAR ---------------------------------------------------------
    bottom = tk.Frame(root, bg="#AB7E02")
    bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
    bottom.grid_columnconfigure(0, weight=0)
    bottom.grid_columnconfigure(1, weight=1)

    def end_game():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        for _ in range(3):
            sock.sendto(b"221", (config.NETWORK_ADDRESS, 7500))
        root.destroy()

    tk.Button(bottom, text="End Game", font=("Arial", 14),
              bg="#AB7E02", fg="white", command=end_game
              ).grid(row=0, column=0, padx=20, pady=10)

    # ---------- LOG AREA (read‑only) --------------------------------------
    log_box = tk.Text(bottom, height=4, bg="#FFFFE0",
                      font=("Arial", 10), state="disabled", wrap="none")
    log_box.grid(row=0, column=1, sticky="ew", padx=10)

    timer_lbl = tk.Label(bottom, font=("Arial", 24),
                         fg="black", bg="#AB7E02")
    timer_lbl.grid(row=1, column=1, pady=5)

    # -----------------------------------------------------------------------
    #  THREAD‑SAFE LOGGING
    # -----------------------------------------------------------------------
    log_q = queue.Queue()

    def add_to_log(msg):
        log_box.config(state="normal")
        log_box.insert("end", msg + "\n")
        log_box.config(state="disabled")
        log_box.see("end")

    def poll_log_queue():
        while not log_q.empty():
            add_to_log(log_q.get())
        root.after(100, poll_log_queue)   # keep polling

    poll_log_queue()  # start the polling loop

    # this function is passed to the UDP thread -----------------------------
    def log_event(msg):
        log_q.put(msg)

    # -----------------------------------------------------------------------
    score_labels  = {"Red": red_score,  "Green": green_score}
    player_frames = {"Red": red_players, "Green": green_players}

    threading.Thread(target=udpServer.run_server,
                     args=(score_labels, player_frames, log_event),
                     daemon=True).start()

    # kick the traffic generator
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.sendto(b"202", (config.NETWORK_ADDRESS, 7500))
    print("Sent '202' to traffic generator")

    # -----------------------------------------------------------------------
    def update_timer(sec):
        if sec > 0:
            mins, secs = divmod(sec, 60)
            timer_lbl.config(text=f"{mins:02d}:{secs:02d}")
            root.after(1000, update_timer, sec-1)
        else:
            timer_lbl.config(text="Game Over")
    update_timer(360)

# ---------------------------------------------------------------------------
def handle_score_event(player_id, team, score_lbl, players_fr):
    if player_id not in player_scores:
        return
    p = player_scores[player_id]
    p["score"] += 100
    if not p["codename"].startswith("B "):
        p["codename"] = "B " + p["codename"]

    score_lbl.config(text=f"Score: {sum(
        pp['score'] for pp in player_scores.values() if pp['team']==team)}")

    for w in players_fr.winfo_children(): w.destroy()
    for pid, pdata in sorted(player_scores.items(),
                             key=lambda x: -x[1]["score"]):
        if pdata["team"] == team:
            tk.Label(players_fr,
                     text=f"ID: {pid} | Name: {pdata['codename']} | "
                          f"Score: {pdata['score']}",
                     bg=players_fr["bg"], fg="#FFFF33",
                     font=("Arial", 12)
                     ).pack(anchor="w", pady=2)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Player Actions")
    root.geometry("800x600")
    start_game(root)
    root.mainloop()



















