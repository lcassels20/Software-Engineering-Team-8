import socket
import random
import time
import config  # Use shared network address

bufferSize = 1024
network_address = config.NETWORK_ADDRESS
game_listen_port = 7501

print("\nThis program will generate some test traffic for 2 players on the red")
print("team as well as 2 players on the green team.\n")

try:
    red1    = str(int(input('Enter equipment ID of Red player 1 ==> ')))
    red2    = str(int(input('Enter equipment ID of Red player 2 ==> ')))
    green1  = str(int(input('Enter equipment ID of Green player 1 ==> ')))
    green2  = str(int(input('Enter equipment ID of Green player 2 ==> ')))
except ValueError:
    print("All equipment IDs must be numeric.")
    exit()

# Single socket for all sending/receiving
UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDPSocket.settimeout(150)
UDPSocket.bind((network_address, 0))  # Let OS assign port

print("Traffic generator bound on:", UDPSocket.getsockname())
print("\nWaiting for start from game_software...")

# Wait for 202 signal from game
while True:
    try:
        data, addr = UDPSocket.recvfrom(bufferSize)
        msg = data.decode('utf-8')
        print("Received from game software:", msg)
        if msg == "202":
            break
    except socket.timeout:
        print("Timed out waiting for game start.")
        exit()

print("Starting traffic simulation...")
time.sleep(0.5)  # Let server fully initialize

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

    print(f"\nTransmitting to game: {message}")
    UDPSocket.sendto(message.encode(), (network_address, game_listen_port))

    try:
        response, addr = UDPSocket.recvfrom(bufferSize)
        print("  ↳ Response from game:", response.decode())
    except socket.timeout:
        print("No response. Ending simulation.")
        break

    if response.decode().strip() == "221":
        break

    counter += 1
    time.sleep(random.randint(1, 3))

print("Traffic simulation complete.")







