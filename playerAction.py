"""
Player‑action screen
────────────────────
• Team panels, scoring, six‑minute timer, End‑Game button.
• Live, scrollable event log fed by the UDP server thread.
• ***No music functionality (randomMusic import/thread removed).***
"""
import tkinter as tk
from database import get_connection
import socket, threading, queue
import config, udpServer

player_scores = {}

# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────
def fetch_players():
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT player_id, name, equipment_id, team "
                "FROM players ORDER BY id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def create_scrollable_frame(parent, height):
    canvas = tk.Canvas(parent, bg=parent["bg"], highlightthickness=0,
                       height=height)
    vsb    = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame  = tk.Frame(canvas, bg=parent["bg"])
    frame.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack  (side="right", fill="y")
    return frame
# ──────────────────────────────────────────────────────────────────────


def launch_game_screen(root, players=None):          # preferred name
    """Builds the score screen and kicks everything off."""
    global player_scores
    for w in root.winfo_children():
        w.destroy()

    if players is None:
        players = fetch_players()

    # Build player‑scores dict keyed by equipment‑ID
    player_scores.clear()
    for pid, name, equip, team in players:
        try:
            eq = int(equip)
            player_scores[eq] = {"codename": name,
                                 "score": 0,
                                 "team":  team}
        except ValueError:
            continue

    red_team   = [p for p in players if p[3] == "Red"]
    green_team = [p for p in players if p[3] == "Green"]

    # ───────── layout – two panels + bottom bar ─────────
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    def make_panel(bg, logo_file, rows):
        frame = tk.Frame(root, bg=bg, highlightthickness=2,
                         highlightbackground="#FFFF33")
        score_lbl = tk.Label(frame, text="Score: 0",
                             font=("Arial", 16), bg=bg, fg="#FFFF33")
        score_lbl.pack(pady=5)

        logo = tk.PhotoImage(file=logo_file)
        tk.Label(frame, image=logo, bg=bg).pack(pady=10)
        frame.logo = logo  # keep reference

        plist = create_scrollable_frame(frame, 250)
        for r in rows:
            tk.Label(plist,
                     text=f"ID: {r[0]} | Name: {r[1]} | Equipment: {r[2]}",
                     font=("Arial", 12), bg=bg, fg="#FFFF33"
                     ).pack(anchor="w", pady=2)
        return frame, score_lbl, plist

    red_frame , red_score , red_list   = make_panel("#592020",
                                                   "redTeam.png",   red_team)
    green_frame, green_score, green_list = make_panel("#20592e",
                                                     "greenTeam.png", green_team)
    red_frame.grid  (row=0, column=0, sticky="nsew")
    green_frame.grid(row=0, column=1, sticky="nsew")

    # ───────── bottom bar ─────────
    bottom = tk.Frame(root, bg="#AB7E02")
    bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
    bottom.grid_columnconfigure(0, weight=0)   # End Game
    bottom.grid_columnconfigure(1, weight=1)   # log box
    bottom.grid_columnconfigure(2, weight=0)   # timer

    # live log Text (read‑only)
    log_box = tk.Text(bottom, height=4, bg="#FFFFE0",
                      font=("Arial", 10), wrap="none", state="disabled")
    log_box.grid(row=0, column=1, sticky="ew", padx=10)

    # timer label
    timer_lbl = tk.Label(bottom, text="", font=("Arial", 24),
                         fg="black", bg="#AB7E02")
    timer_lbl.grid(row=0, column=2, padx=10)

    # thread‑safe queue + flusher
    log_q = queue.Queue()

    def log_event(line: str):
        log_q.put(line)

    def flush_queue():
        while not log_q.empty():
            line = log_q.get()
            log_box.config(state="normal")
            log_box.insert("end", line + "\n")
            log_box.config(state="disabled")
            log_box.see("end")
        root.after(100, flush_queue)

    flush_queue()                       # start the cycle

    # End‑Game button
    def end_game():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            for _ in range(3):
                s.sendto(b"221", (config.NETWORK_ADDRESS, 7500))
        root.destroy()

    tk.Button(bottom, text="End Game", font=("Arial", 14),
              bg="#AB7E02", fg="white", command=end_game
              ).grid(row=0, column=0, padx=20, pady=10)

    # ───────── UDP server thread ─────────
    score_labels  = {"Red": red_score,  "Green": green_score}
    player_frames = {"Red": red_list,   "Green": green_list}

    threading.Thread(
        target=udpServer.run_server,
        args=(score_labels, player_frames, log_event),
        daemon=True
    ).start()

    # ─────────  send “202” start signal  ─────────
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.sendto(b"202", (config.NETWORK_ADDRESS, 7500))
    print("Sent '202' to traffic generator")

    # ─────────  six‑minute countdown  ─────────
    def update_timer(sec):
        if sec > 0:
            m, s = divmod(sec, 60)
            timer_lbl.config(text=f"{m:02d}:{s:02d}")
            root.after(1000, update_timer, sec - 1)
        else:
            timer_lbl.config(text="Game Over")
            for _ in range(3):
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.sendto(b"221", (config.NETWORK_ADDRESS, 7500))
    update_timer(360)


# keep old name too so existing imports keep working
start_game = launch_game_screen


# ─────────────────── scoring routine (unchanged) ────────────────────
def handle_score_event(player_id, team, score_label, players_frame):
    if player_id not in player_scores:
        return
    pdata = player_scores[player_id]
    pdata["score"] += 100
    if not pdata["codename"].startswith("B "):
        pdata["codename"] = "B " + pdata["codename"]

    team_total = sum(p["score"] for p in player_scores.values()
                     if p["team"] == team)
    score_label.config(text=f"Score: {team_total}")

    for w in players_frame.winfo_children():
        w.destroy()
    for pid, rec in sorted(player_scores.items(),
                           key=lambda x: -x[1]["score"]):
        if rec["team"] == team:
            tk.Label(players_frame,
                     text=f"ID: {pid} | Name: {rec['codename']} | "
                          f"Score: {rec['score']}",
                     font=("Arial", 12),
                     bg=players_frame["bg"], fg="#FFFF33"
                     ).pack(anchor="w", pady=2)


# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Player Actions")
    root.geometry("800x600")
    launch_game_screen(root)
    root.mainloop()























