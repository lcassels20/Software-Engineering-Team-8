import socket
import config
from playerAction import handle_score_event, player_scores, log_event  # ⬅️ NEW import

def run_server(score_labels=None, player_frames=None):
    print(">>> run_server() called")
    log_event(">>> UDP Server Started")

    localIP = config.NETWORK_ADDRESS
    localPort = 7501  # Receiving port
    bufferSize = 1024

    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening on", localIP, ":", localPort)
    log_event(f"UDP server listening on {localIP}:{localPort}")
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
                    log_event(f"Red player {shooter_id} scored on Green base!")
                    print(f"Red player {shooter_id} scored on Green base!")
                    handle_score_event(shooter_id, "Red", score_labels["Red"], player_frames["Red"])
                    UDPServerSocket.sendto(b"43", address)
                    continue

                elif target_id == 53 and player_scores[shooter_id]["team"] == "Green":
                    log_event(f"Green player {shooter_id} scored on Red base!")
                    print(f"Green player {shooter_id} scored on Red base!")
                    handle_score_event(shooter_id, "Green", score_labels["Green"], player_frames["Green"])
                    UDPServerSocket.sendto(b"53", address)
                    continue

                print(f"Parsed shooter_id: {shooter_id}, target_id: {target_id}")
                log_event(f"{shooter_id} hit {target_id}")

            except ValueError:
                print("Invalid IDs in message:", message)
                log_event("Invalid hit message format received.")
                UDPServerSocket.sendto(b"INVALID", address)
                continue

            if shooter_id in player_scores:
                team = player_scores[shooter_id]["team"]
                print(f"Handling event: {shooter_id} (shooter) hit {target_id} on team {team}")
                handle_score_event(
                    shooter_id,
                    team,
                    score_labels[team],
                    player_frames[team]
                )
                UDPServerSocket.sendto(str(target_id).encode(), address)
            else:
                print(f"Shooter ID {shooter_id} not found in player_scores.")
                log_event(f"Shooter ID {shooter_id} not found.")
                UDPServerSocket.sendto(b"UNKNOWN SHOOTER", address)

        elif message.strip() == "221":
            print("Game over signal received. Sending '221'")
            log_event("Game over signal received.")
            UDPServerSocket.sendto(b"221", address)

        else:
            print(f"Message '{message.strip()}' not understood. Sending default reply 'OK'")
            log_event(f"Unknown message received: {message.strip()}")
            UDPServerSocket.sendto(b"OK", address)

if __name__ == "__main__":
    run_server()










































