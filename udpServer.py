import socket
import config

def run_server(score_labels=None, player_frames=None):
    from playerAction import handle_score_event, player_scores

    localIP = config.NETWORK_ADDRESS
    localPort = 7501  # ✅ CORRECT: game listens on 7501
    bufferSize = 1024

    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening on", localIP, ":", localPort)

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0].decode()
        address = bytesAddressPair[1]

        print("UDP Server received message:", message)
        print("Current player_scores keys:", list(player_scores.keys()))

        if ":" in message and score_labels and player_frames:
            shooter_str, target_str = message.split(":")
            try:
                shooter_id = int(shooter_str)
                target_id = int(target_str)
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
                reply = str(target_id)
            else:
                print("Shooter ID not found in player_scores:", shooter_id)
                reply = "INVALID"

            UDPServerSocket.sendto(reply.encode(), address)

        elif message.strip() == "221":
            UDPServerSocket.sendto(b"221", address)
        else:
            UDPServerSocket.sendto(b"OK", address)

if __name__ == "__main__":
    run_server()





