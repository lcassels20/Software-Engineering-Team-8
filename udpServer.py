import socket
import config

def run_server(score_labels=None, player_frames=None, event_label=None, player_scores_ref=None):
    from playerAction import handle_score_event

    print(">>> run_server() called")
    localIP = config.NETWORK_ADDRESS
    localPort = 7501  # Receiving port
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
        if player_scores_ref:
            print("Current player_scores keys:", list(player_scores_ref.keys()))

        if ":" in message and score_labels and player_frames and player_scores_ref:
            try:
                shooter_str, target_str = message.split(":")
                shooter_id = int(shooter_str)
                target_id = int(target_str)

                if shooter_id not in player_scores_ref:
                    print(f"Shooter ID {shooter_id} not found in player_scores.")
                    UDPServerSocket.sendto(b"UNKNOWN SHOOTER", address)
                    continue

                shooter_name = player_scores_ref[shooter_id]["codename"]

                if target_id == 43 and player_scores_ref[shooter_id]["team"] == "Red":
                    print(f"Red player {shooter_id} scored on Green base!")
                    handle_score_event(shooter_id, "Red", score_labels["Red"], player_frames["Red"])
                    if event_label:
                        event_label.config(text=f"{shooter_name} scored on Green base!")
                    UDPServerSocket.sendto(b"43", address)
                    continue
                elif target_id == 53 and player_scores_ref[shooter_id]["team"] == "Green":
                    print(f"Green player {shooter_id} scored on Red base!")
                    handle_score_event(shooter_id, "Green", score_labels["Green"], player_frames["Green"])
                    if event_label:
                        event_label.config(text=f"{shooter_name} scored on Red base!")
                    UDPServerSocket.sendto(b"53", address)
                    continue

                print(f"Parsed shooter_id: {shooter_id}, target_id: {target_id}")
            except ValueError:
                print("Invalid IDs in message:", message)
                UDPServerSocket.sendto(b"INVALID", address)
                continue

            team = player_scores_ref[shooter_id]["team"]
            print(f"Handling event: {shooter_id} (shooter) hit {target_id} (target) on team {team}")
            handle_score_event(
                shooter_id,
                team,
                score_labels[team],
                player_frames[team]
            )

            if event_label:
                event_label.config(text=f"{shooter_name} hit {target_id}")

            print(f"Sending hit acknowledgment: {target_id}")
            UDPServerSocket.sendto(str(target_id).encode(), address)

        elif message.strip() == "221":
            print("Game over signal received. Sending '221'")
            UDPServerSocket.sendto(b"221", address)
        else:
            print(f"Message '{message.strip()}' not understood. Sending default reply 'OK'")
            UDPServerSocket.sendto(b"OK", address)

if __name__ == "__main__":
    run_server()















