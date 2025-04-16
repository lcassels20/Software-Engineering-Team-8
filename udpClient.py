import socket
import config

def run_client():
    message = b"Hello UDP Server"
    serverAddressPort = (config.NETWORK_ADDRESS, 7501)
    bufferSize = 1024

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        UDPClientSocket.sendto(message, serverAddressPort)
        print("UDP Client sent: Hello UDP Server to", serverAddressPort)
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        print("Message from Server:", msgFromServer[0].decode())
    except Exception as e:
        print("UDP Client failed to communicate:", e)
    finally:
        UDPClientSocket.close()

if __name__ == "__main__":
    run_client()


