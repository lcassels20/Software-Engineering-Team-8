import socket
import config
from playerAction import handle_score_event, handle_base_hit, player_scores

def run_server(score_labels=None, player_frames=None):
    localIP = config.NETWORK_ADDRESS
    localPort = 7501
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

            if target_id == 43 or target_id == 53:
                if shooter_id in player_scores:
                    print(f"Base hit: {shooter_id} tagged base {target_id}")
                    team = player_scores[shooter_id]["team"]
                    handle_base_hit(shooter_id, team, score_labels[team], player_frames[team])
                    reply = str(target_id)
                else:
                    print("Shooter ID not found for base hit:", shooter_id)
                    reply = "INVALID"
            elif shooter_id in player_scores:
                shooter_team = player_scores[shooter_id]["team"]
                target_team = None
                for pid, pdata in player_scores.items():
                    if pid == target_id:
                        target_team = pdata["team"]
                        break
                if target_team == shooter_team:
                    print(f"{shooter_id} tagged their own team member {target_id} — penalty")
                    player_scores[shooter_id]["score"] -= 10
                    reply = str(shooter_id)
                else:
                    print(f"Handling event: {shooter_id} (shooter) hit {target_id} (target) on opposing team")
                    handle_score_event(
                        shooter_id,
                        shooter_team,
                        score_labels[shooter_team],
                        player_frames[shooter_team]
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








