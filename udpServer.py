import socket
import config

def run_server(score_labels=None, player_frames=None):
    from playerAction import handle_score_event, player_scores
    localIP = config.NETWORK_ADDRESS
    localPort = 7501  # Receiving port
    bufferSize = 1024

    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening on", localIP, ":", localPort)

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0].decode()
        address = bytesAddressPair[1]
        print("UDP Server received message:", message)

        # Handle score event if it's an ID pair
        if ":" in message and score_labels and player_frames:
            shooter_str, target_str = message.split(":")
            try:
                shooter_id = int(shooter_str)
            except ValueError:
                print("Invalid shooter ID:", shooter_str)
                continue

            if shooter_id in player_scores:
                team = player_scores[shooter_id]["team"]
                handle_score_event(
                    shooter_id,
                    team,
                    score_labels[team],
                    player_frames[team]
                )
            else:
                print("Shooter ID not found in player_scores:", shooter_id)

        # Always reply
        reply = "OK" if message.strip() != "221" else "221"
        UDPServerSocket.sendto(reply.encode(), address)

if __name__ == "__main__":
    run_server()

