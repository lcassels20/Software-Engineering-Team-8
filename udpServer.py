import socket
import config
from log import log_event

def run_server(score_labels=None, player_frames=None):
    from playerAction import handle_score_event, player_scores

    localIP = config.NETWORK_ADDRESS
    localPort = 7501
    bufferSize = 1024

    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    log_event(f"Server started on {localIP}:{localPort}")
    log_event("Waiting for UDP messages...")

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0].decode()
        address = bytesAddressPair[1]

        log_event(f"Received message: {message}")

        if ":" in message and score_labels and player_frames:
            try:
                shooter_str, target_str = message.split(":")
                shooter_id = int(shooter_str)
                target_id = int(target_str)

                if target_id == 43 and player_scores[shooter_id]["team"] == "Red":
                    log_event(f"Red player {shooter_id} scored on Green base")
                    handle_score_event(shooter_id, "Red", score_labels["Red"], player_frames["Red"])
                    UDPServerSocket.sendto(b"43", address)
                    continue

                elif target_id == 53 and player_scores[shooter_id]["team"] == "Green":
                    log_event(f"Green player {shooter_id} scored on Red base")
                    handle_score_event(shooter_id, "Green", score_labels["Green"], player_frames["Green"])
                    UDPServerSocket.sendto(b"53", address)
                    continue

                log_event(f"Parsed shooter_id: {shooter_id}, target_id: {target_id}")

            except ValueError:
                log_event(f"Invalid message format: {message}")
                UDPServerSocket.sendto(b"INVALID", address)
                continue

            if shooter_id in player_scores:
                team = player_scores[shooter_id]["team"]
                log_event(f"Player {shooter_id} hit {target_id} (Team {team})")
                handle_score_event(shooter_id, team, score_labels[team], player_frames[team])
                UDPServerSocket.sendto(str(target_id).encode(), address)
            else:
                log_event(f"Unknown shooter ID: {shooter_id}")
                UDPServerSocket.sendto(b"UNKNOWN SHOOTER", address)

        elif message.strip() == "221":
            log_event("Game over signal received.")
            UDPServerSocket.sendto(b"221", address)

        else:
            log_event(f"Unrecognized message: '{message.strip()}'")
            UDPServerSocket.sendto(b"OK", address)

if __name__ == "__main__":
    run_server()









































































