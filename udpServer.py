import socket, config

def run_server(score_labels=None, player_frames=None, log_event=None):
    try:
        from playerAction import handle_score_event, player_scores

        def log(line: str):
            print(line)
            if log_event:
                log_event(line)

        localIP = config.NETWORK_ADDRESS
        localPort = 7501
        buf = 1024

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((localIP, localPort))
        log(f"UDP server up and listening on {localIP}:{localPort}")

        while True:
            try:
                log("Waiting for UDP message...")
                data, addr = sock.recvfrom(buf)
                log(f"Received from {addr}: {data}")
                msg = data.decode().strip()
                log(f"Decoded message: {msg}")
            except Exception as e:
                log(f"Error while receiving data: {e}")
                continue

            if ":" in msg:
                try:
                    shooter_str, target_str = msg.split(":")
                    shooter_id = int(shooter_str)
                    target_id  = int(target_str)
                except ValueError:
                    log("Malformed message: could not parse shooter/target")
                    sock.sendto(b"INVALID", addr)
                    continue

                if shooter_id not in player_scores:
                    log(f"UNKNOWN SHOOTER: {shooter_id} not in player_scores")
                    sock.sendto(b"UNKNOWN SHOOTER", addr)
                    continue

                if score_labels and player_frames:
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
                else:
                    log(f"Received hit: {shooter_id} -> {target_id}, but GUI not active.")
                    sock.sendto(str(target_id).encode(), addr)

            elif msg == "221":
                log("Game‑over signal received.")
                sock.sendto(b"221", addr)
            else:
                log(f"Unrecognized message format: {msg}")
                sock.sendto(b"OK", addr)

    except Exception as e:
        print("Fatal error in UDP server:", e)


if __name__ == "__main__":
    run_server()



























