import socket
import config

def run_server():
    localIP = config.NETWORK_ADDRESS
    localPort = 7501  # Receiving port
    bufferSize = 1024
    msgFromServer = "Hello UDP Client"
    bytesToSend = msgFromServer.encode()

    # Create UDP socket for receiving data.
    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening on", localIP, ":", localPort)

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        print("UDP Server received message:", message.decode())
        UDPServerSocket.sendto(bytesToSend, address)

if __name__ == "__main__":
    run_server()
