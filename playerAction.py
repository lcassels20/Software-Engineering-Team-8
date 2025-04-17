"""
playerAction.py  –  Team‑score screen with live event log

Fixes (2025‑04‑17):
* Cancel all .after() timers before destroying the window, eliminating
  AttributeError / TclError that killed network traffic.
* Added WM_DELETE_WINDOW handler so closing the window is identical to
  clicking “End Game”.
"""
import tkinter as tk
from database import get_connection
import socket, threading, queue
import config
import udpServer

player_scores = {}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def fetch_players():
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT player_id, name, equipment_id, team FROM players "
                "ORDER BY id")
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
    vsb.pack(side="right", fill="y")
    return frame
# ──────────────────────────────────────────────────────────────────────────────


def start_game(root, players=None):
    """
    Replaces the entire window contents with the live game‑play screen.
    """
    global player_scores
    # wipe whatever was on the root before
    for w in root.winfo_children():
        w.destroy()

    if players is None:
        players = fetch_players()

    # ------------------------------------------------------------------
    # build {equipment_id: {...}} so we can score hits quickly
    # ------------------------------------------------------------------
    player_scores = {}
    for pid, name, equip, team in players:
        try:
            equip_id = int(equip)
            player_scores[equip_id] = {
                "codename": name, "score": 0, "team": team
            }
        except ValueError:
            continue

    red_team   = [p for p in players if p[3] == "Red"]
    green_team = [p for p in players if p[3] == "Green"]

    # ──────────────── layout (2 team panels + bottom bar) ─────────────
    root.grid_rowconfigure(0, weight=1)      # team panels grow
    root.grid_rowconfigure(1, weight=0)      # bottom stays fixed
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    def make_panel(bg, logo_file, team_rows):
        frame = tk.Frame(root, bg=bg, highlightthickness=2,
                         highlightbackground="#FFFF33")
        score_lbl = tk.Label(frame, text="Score: 0",
                             bg=bg, fg="#FFFF33", font=("Arial", 16))
        score_lbl.pack(pady=5)

        logo = tk.PhotoImage(file=logo_file)
        tk.Label(frame, image=logo, bg=bg).pack(pady=10)
        frame.logo = logo                      # keep reference

        plist = create_scrollable_frame(frame, 250)
        for row in team_rows:
            tk.Label(plist,
                     text=f"ID: {row[0]} | Name: {row[1]} | "
                          f"Equipment: {row[2]}",
                     bg=bg, fg="#FFFF33", font=("Arial", 12)
                     ).pack(anchor="w", pady=2)
        return frame, score_lbl, plist

    red_frame , red_score , red_list   = make_panel("#592020",
                                                   "redTeam.png",   red_team)
    green_frame, green_score, green_list = make_panel("#20592e",
                                                     "greenTeam.png", green_team)

    red_frame.grid  (row=0, column=0, sticky="nsew")
    green_frame.grid(row=0, column=1, sticky="nsew")

    # ───────────── bottom bar (End‑Game, log, timer) ──────────────────
    bottom = tk.Frame(root, bg="#AB7E02")
    bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
    bottom.grid_columnconfigure(0, weight=0)   # End Game
    bottom.grid_columnconfigure(1, weight=1)   # log box expands
    bottom.grid_columnconfigure(2, weight=0)   # timer

    # ‑‑‑ live event log (read‑only Text) ‑‑‑
    log_box = tk.Text(bottom, height=4, bg="#FFFFE0",
                      font=("Arial", 10), wrap="none", state="disabled")
    log_box.grid(row=0, column=1, sticky="ew", padx=10)

    timer_lbl = tk.Label(bottom, text="", font=("Arial", 24),
                         fg="black", bg="#AB7E02")
    timer_lbl.grid(row=0, column=2, pady=5, padx=10)

    # ───────────── thread‑safe queues / timers ────────────────────────
    log_q      = queue.Queue()
    after_ids  = []             # **EVERY** root.after() ID stored here

    def log_event(line: str):
        log_q.put(line)

    def flush_queue():
        """
        Pull every queued log line and append to the Text box.
        Reschedules itself every 100 ms while the window exists.
        """
        while not log_q.empty():
            line = log_q.get()
            log_box.config(state="normal")
            log_box.insert("end", line + "\n")
            log_box.config(state="disabled")
            log_box.see("end")
        # schedule the next flush, keep its id
        after_ids.append(root.after(100, flush_queue))

    flush_queue()               # prime the pump

    # ───────────── score‑label dicts for udpServer ‑‑ unchanged ───────
    score_labels  = {"Red": red_score,  "Green": green_score}
    player_frames = {"Red": red_list,   "Green": green_list}

    # ───────────── network thread ‑‑ same server, new log function ────
    threading.Thread(
        target=udpServer.run_server,
        args=(score_labels,
              player_frames,
              log_event,        # give it the logger
              handle_score_event,  # **touches Tk, but has worked fine so far**
              player_scores),
        daemon=True
    ).start()

    # ───────────── send 202 start signal after GUI up ‑────────────────
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.sendto(b"202", (config.NETWORK_ADDRESS, 7500))
    print("Sent '202' to traffic generator")

    # ───────────── 6‑minute countdown timer ‑─────────────────────────
    def update_timer(sec):
        if sec > 0:
            m, s = divmod(sec, 60)
            timer_lbl.config(text=f"{m:02d}:{s:02d}")
            after_ids.append(root.after(1000, update_timer, sec - 1))
        else:
            timer_lbl.config(text="Game Over")
    update_timer(360)

    # ───────────── clean‑exit helper (button & window X) ─────────────
    def end_game():
        # 1) cancel every pending .after() callback BEFORE destroying
        for aft in after_ids:
            try:
                root.after_cancel(aft)
            except tk.TclError:
                pass

        # 2) notify traffic generator
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            for _ in range(3):
                s.sendto(b"221", (config.NETWORK_ADDRESS, 7500))

        # 3) close window
        root.destroy()

    # button + window‑manager close both use the same cleanup
    tk.Button(bottom, text="End Game", font=("Arial", 14),
              bg="#AB7E02", fg="white", command=end_game
              ).grid(row=0, column=0, padx=20, pady=10)
    root.protocol("WM_DELETE_WINDOW", end_game)

# ──────────────────────────────────────────────────────────────────────────────
# Scoring – unchanged
# ──────────────────────────────────────────────────────────────────────────────
def handle_score_event(player_id, team, score_label, players_frame):
    if player_id not in player_scores:
        print(f"Player ID {player_id} not found.")
        return

    pdata = player_scores[player_id]
    pdata["score"] += 100
    if not pdata["codename"].startswith("B "):
        pdata["codename"] = "B " + pdata["codename"]

    team_score = sum(p["score"] for p in player_scores.values()
                     if p["team"] == team)
    score_label.config(text=f"Score: {team_score}")

    # rebuild sorted list
    for w in players_frame.winfo_children():
        w.destroy()
    for pid, rec in sorted(player_scores.items(),
                           key=lambda x: -x[1]["score"]):
        if rec["team"] == team:
            tk.Label(players_frame,
                     text=f"ID: {pid} | Name: {rec['codename']} | "
                          f"Score: {rec['score']}",
                     bg=players_frame["bg"], fg="#FFFF33",
                     font=("Arial", 12)
                     ).pack(anchor="w", pady=2)

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Player Actions")
    root.geometry("800x600")
    start_game(root)
    root.mainloop()






















