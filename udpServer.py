"""
UDP hit‑processing server
─────────────────────────
• Signature expanded → run_server(score_labels, player_frames, log_event=None)
• If `log_event` is supplied, every log line is forwarded to the GUI log;
  otherwise it just prints to the console (exactly as before).
• The scoring & acknowledgement logic is *identical* to your last
  working version, so the traffic generator sees the same responses.
"""
import socket, config

def run_server(score_labels=None, player_frames=None, log_event=None):
    from playerAction import handle_score_event, player_scores

    def log(line: str):
        print(line)
        if log_event:
            log_event(line)

    localIP  = config.NETWORK_ADDRESS
    localPort = 7501
    buf      = 1024

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((localIP, localPort))
    log(f"UDP server up and listening on {localIP}:{localPort}")

    while True:
        data, addr = sock.recvfrom(buf)
        msg = data.decode().strip()
        log(f"\nUDP Server received message: {msg}")

        if ":" in msg and score_labels and player_frames:
            try:
                shooter_str, target_str = msg.split(":")
                shooter_id = int(shooter_str)
                target_id  = int(target_str)
            except ValueError:
                sock.sendto(b"INVALID", addr)
                continue

            if shooter_id not in player_scores:
                sock.sendto(b"UNKNOWN SHOOTER", addr)
                continue

            team = player_scores[shooter_id]["team"]

            # base hits
            if target_id == 43 and team == "Red":
                log(f"Red base hit by player {shooter_id}")
                handle_score_event(shooter_id, "Red",
                                   score_labels["Red"],
                                   player_frames["Red"])
                sock.sendto(b"43", addr)
                continue
            if target_id == 53 and team == "Green":
                log(f"Green base hit by player {shooter_id}")
                handle_score_event(shooter_id, "Green",
                                   score_labels["Green"],
                                   player_frames["Green"])
                sock.sendto(b"53", addr)
                continue

            # normal hit
            log(f"Player {shooter_id} hit Player {target_id}")
            handle_score_event(shooter_id, team,
                               score_labels[team],
                               player_frames[team])
            sock.sendto(str(target_id).encode(), addr)

        elif msg == "221":
            log("Game‑over signal received.")
            sock.sendto(b"221", addr)
        else:
            sock.sendto(b"OK", addr)

if __name__ == "__main__":
    run_server()

























