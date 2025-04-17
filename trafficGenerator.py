import socket
import random
import time

# Ask for network address
def get_network_address():
    print("Select network address (default is 127.0.0.1)")
    new_address = input("Enter new network address or press enter for default: ")
    return new_address.strip() if new_address else "127.0.0.1"

bufferSize = 1024
network_address = get_network_address()
game_listen_port = 7501  # Where the game listens for hits

print('\nThis program will generate some test traffic for 2 players on the red')
print('team as well as 2 players on the green team.\n')

red1 = input('Enter equipment ID of Red player 1 ==> ')
red2 = input('Enter equipment ID of Red player 2 ==> ')
green1 = input('Enter equipment ID of Green player 1 ==> ')
green2 = input('Enter equipment ID of Green player 2 ==> ')

# Create socket (DO NOT bind)
UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDPSocket.settimeout(150)  # wait for game to send startup messages

print("\nWaiting for start from game_software...")

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

print('Starting traffic simulation...\n')

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

    print(f"Transmitting to game: {message}")
    print(f"  ↳ Sending to ({network_address}, {game_listen_port})")
    UDPSocket.sendto(message.encode(), (network_address, game_listen_port))

    try:
        print("  ↳ Waiting for response from game...")
        received_data, address = UDPSocket.recvfrom(bufferSize)
        received_data = received_data.decode('utf-8')
        print(f"  ↳ Received from game: {received_data}")
    except socket.timeout:
        print("No response from game software (timed out). Ending traffic.")
        break

    print('')
    counter += 1
    if received_data == '221':
        break

    time.sleep(random.randint(1, 3))

print("Program complete.")
UDPSocket.close()





