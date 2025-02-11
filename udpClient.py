import socket

def get_network_address():
	print("Select network address (default is 127.0.0.1)")
	new_address = input("Enter new network address or press enter for default:")
	return new_address.strip() if new_address else "127.0.0.1"

client_network_address = get_network_address()
msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = (client_network_address, 7501)
bufferSize          = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0])

print(msg)