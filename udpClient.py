import socket
import config

def run_client():
    # Create a UDP socket for the client.
    UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # The client sends its message to the server's receiving port (7501).
    serverAddressPort = (config.NETWORK_ADDRESS, 7502)
    msgFromClient = "Hello UDP Server"
    bytesToSend = msgFromClient.encode()
    
    # Send the message to the server.
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    print(f"UDP Client sent: {msgFromClient} to {serverAddressPort}")
    
    # Wait for the server's response.
    bufferSize = 1024
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    print("UDP Client received:", msgFromServer[0].decode())

if __name__ == "__main__":
    run_client()
