import socket
import config

def run_server(score_labels=None, player_frames=None):
    from playerAction import handle_score_event, player_scores

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
        print("Current player_scores keys:", list(player_scores.keys()))

        if ":" in message and score_labels and player_frames:
            try:
                shooter_str, target_str = message.split(":")
                shooter_id = int(shooter_str)
                target_id = int(target_str)
                print(f"Parsed shooter_id: {shooter_id}, target_id: {target_id}")
            except ValueError:
                print("Invalid IDs in message:", message)
                UDPServerSocket.sendto(b"INVALID", address)
                continue

            if shooter_id in player_scores:
                team = player_scores[shooter_id]["team"]
                print(f"Handling event: {shooter_id} (shooter) hit {target_id} (target) on team {team}")
                handle_score_event(
                    shooter_id,
                    team,
                    score_labels[team],
                    player_frames[team]
                )

                # Send back the equipment ID of the player who got hit
                print(f"Sending hit acknowledgment: {target_id}")
                UDPServerSocket.sendto(str(target_id).encode(), address)
            else:
                print(f"Shooter ID {shooter_id} not found in player_scores.")
                UDPServerSocket.sendto(b"UNKNOWN SHOOTER", address)

        elif message.strip() == "221":
            print("Game over signal received. Sending '221'")
            UDPServerSocket.sendto(b"221", address)
        else:
            print(f"Message '{message.strip()}' not understood. Sending default reply 'OK'")
            UDPServerSocket.sendto(b"OK", address)

if __name__ == "__main__":
    run_server()













