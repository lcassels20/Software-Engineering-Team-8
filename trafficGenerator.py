import socket
import random
import time

def get_network_address():
	print("Select network address (default is 127.0.0.1)")
	new_address = input("Enter new network address or press enter for default:")
	return new_address.strip() if new_address else "127.0.0.1"

bufferSize  = 1024
network_address = get_network_address()
game_listen_port = 7501  # the game's listening port
local_receive_port = 7500  # the generator's bound port for replies

print('this program will generate some test traffic for 2 players on the red ')
print('team as well as 2 players on the green team')
print('')

red1 = input('Enter equipment id of red player 1 ==> ')
red2 = input('Enter equipment id of red player 2 ==> ')
green1 = input('Enter equipment id of green player 1 ==> ')
green2 = input('Enter equipment id of green player 2 ==> ')

# Use a single socket for sending and receiving
UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPSocket.settimeout(150)  # wait long enough for game start
UDPSocket.bind((network_address, local_receive_port))

# wait for start from game software
print("\nwaiting for start from game_software")

start_signal_received = False
while not start_signal_received:
	try:
		received_data, address = UDPSocket.recvfrom(bufferSize)
		received_data = received_data.decode('utf-8')
		print("Received from game software:", received_data)
		if received_data == "202":
			start_signal_received = True
	except socket.timeout:
		print("No response from game software (timed out). Exiting.")
		exit()

print('')

# create events, random player and order
counter = 0

while True:
	redplayer = random.choice([red1, red2])
	greenplayer = random.choice([green1, green2])

	if random.randint(0, 1) == 0:
		message = f"{redplayer}:{greenplayer}"
	else:
		message = f"{greenplayer}:{redplayer}"

	if counter == 10:
		message = f"{redplayer}:43"
	if counter == 20:
		message = f"{greenplayer}:53"

	print("transmitting to game:", message)
	UDPSocket.sendto(message.encode(), (network_address, game_listen_port))

	try:
		received_data, address = UDPSocket.recvfrom(bufferSize)
		received_data = received_data.decode('utf-8')
		print("Received from game software:", received_data)
	except socket.timeout:
		print("No response from game software (timed out). Ending traffic.")
		break

	print('')
	counter += 1
	if received_data == '221':
		break
	time.sleep(random.randint(1, 3))

print("program complete")
















