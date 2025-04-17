import socket, config

def run_server(score_labels=None,
               player_frames=None,
               log_event=None,
               handle_score_event=None,
               player_scores=None):
    """
    score_labels / player_frames‑‑same as before (for score updating)
    log_event           – callable(str)  -> push a line to GUI log (thread‑safe)
    handle_score_event  – original function from playerAction.py
    player_scores       – shared dict from playerAction.py
    """
    localIP, localPort = config.NETWORK_ADDRESS, 7501
    buf = 1024

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((localIP, localPort))
    print("UDP server listening on", localIP, ":", localPort)

    def log(msg):
        print(msg)
        if log_event:
            log_event(msg)

    while True:
        data, addr = sock.recvfrom(buf)
        msg = data.decode().strip()
        log(f"\nUDP Server received message: {msg}")

        # ----- original scoring logic (unchanged) --------------------------
        if ":" in msg and score_labels and player_frames \
           and handle_score_event and player_scores:
            try:
                shooter_str, target_str = msg.split(":")
                shooter_id = int(shooter_str)
                target_id  = int(target_str)

                if shooter_id not in player_scores:
                    sock.sendto(b"UNKNOWN SHOOTER", addr)
                    continue

                team = player_scores[shooter_id]["team"]

                if target_id == 43 and team == "Red":
                    handle_score_event(shooter_id, "Red",
                                       score_labels["Red"],
                                       player_frames["Red"])
                    log(f"Red base hit by player {shooter_id}")
                    sock.sendto(b"43", addr)
                    continue
                if target_id == 53 and team == "Green":
                    handle_score_event(shooter_id, "Green",
                                       score_labels["Green"],
                                       player_frames["Green"])
                    log(f"Green base hit by player {shooter_id}")
                    sock.sendto(b"53", addr)
                    continue

                # regular player‑on‑player hit
                handle_score_event(shooter_id, team,
                                   score_labels[team],
                                   player_frames[team])
                log(f"Player {shooter_id} hit Player {target_id} ({team})")
                sock.sendto(str(target_id).encode(), addr)

            except ValueError:
                sock.sendto(b"INVALID", addr)

        elif msg == "221":
            log("Game‑over signal received.")
            sock.sendto(b"221", addr)
        else:
            sock.sendto(b"OK", addr)

if __name__ == "__main__":
    run_server()























