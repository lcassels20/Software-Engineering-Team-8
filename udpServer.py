import socket
import config

def run_server(score_labels=None, player_frames=None, log_event=None):
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

        if log_event:
            log_event(f"UDP: {message}")

        UDPServerSocket.sendto(b"OK", address)

if __name__ == "__main__":
    run_server()





















