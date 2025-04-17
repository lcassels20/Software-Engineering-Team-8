import socket
import config

def run_server(score_labels=None, player_frames=None, log_event=None):
    from playerAction import handle_score_event, player_scores

    print(">>> run_server() called")
    localIP = config.NETWORK_ADDRESS
    localPort = 7501
    bufferSize = 1024

    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening on", localIP, ":", localPort)
    print(">>> Waiting for messages...")

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0].decode()
        address = bytesAddressPair[1]

        print("\nUDP Server received message:", message)
        print("Current player_scores keys:", list(player_scores.keys()))

        if ":" in message and score_labels and player_frames:
            try:
                shooter_str, target_str = message.split(":")
                shooter_id = int(shooter_str)
                target_id = int(target_str)

                if target_id == 43 and player_scores[shooter_id]["team"] == "Red":
                    handle_score_event(shooter_id, "Red", score_labels["Red"], player_frames["Red"])
                    if log_event:
                        log_event(f"Red base hit by player {shooter_id}")
                    UDPServerSocket.sendto(b"43", address)
                    continue
                elif target_id == 53 and player_scores[shooter_id]["team"] == "Green":
                    handle_score_event(shooter_id, "Green", score_labels["Green"], player_frames["Green"])
                    if log_event:
                        log_event(f"Green base hit by player {shooter_id}")
                    UDPServerSocket.sendto(b"53", address)
                    continue

                if shooter_id in player_scores:
                    team = player_scores[shooter_id]["team"]
                    handle_score_event(shooter_id, team, score_labels[team], player_frames[team])
                    if log_event:
                        log_event(f"Player {shooter_id} hit Player {target_id} ({team} team)")
                    UDPServerSocket.sendto(str(target_id).encode(), address)
                else:
                    UDPServerSocket.sendto(b"UNKNOWN SHOOTER", address)
            except ValueError:
                UDPServerSocket.sendto(b"INVALID", address)
        elif message.strip() == "221":
            if log_event:
                log_event("Game over signal received.")
            UDPServerSocket.sendto(b"221", address)
        else:
            UDPServerSocket.sendto(b"OK", address)

if __name__ == "__main__":
    run_server()



















