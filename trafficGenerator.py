import socket
import random
import time
import select

print("Select network address (default is 127.0.0.1)")
print("Enter new network address or press enter for default:", end=' ')
ip = input().strip()
if ip == "":
    ip = "127.0.0.1"

game_ip = ip
send_port = 7500
receive_port = 7501
bufferSize = 1024

print("this program will generate some test traffic for 2 players on the red ")
print("team as well as 2 players on the green team\n")

red1 = input("Enter equipment id of red player 1 ==> ").strip()
red2 = input("Enter equipment id of red player 2 ==> ").strip()
green1 = input("Enter equipment id of green player 1 ==> ").strip()
green2 = input("Enter equipment id of green player 2 ==> ").strip()

# Set up sending socket
UDPSocketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set up receiving socket
UDPServerSocketReceive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPServerSocketReceive.bind(("", 0))

# Send initial setup messages
startup_messages = ["EQ12345", red1, red2, green1, green2]
for msg in startup_messages:
    UDPSocketSend.sendto(msg.encode(), (game_ip, send_port))
    time.sleep(0.2)

# Wait for game to send "202"
print("\nwaiting for start from game_software")
start_received = False
UDPServerSocketReceive.setblocking(0)

timeout = time.time() + 20  # 20 sec timeout
while time.time() < timeout:
    ready = select.select([UDPServerSocketReceive], [], [], 1)
    if ready[0]:
        data, addr = UDPServerSocketReceive.recvfrom(bufferSize)
        message = data.decode().strip()
        print("Received from game software:", message)
        if message == "202":
            start_received = True
            break

if not start_received:
    print("Timeout waiting for game start.")
    exit()

# Now simulate traffic
players = [red1, red2, green1, green2]
print()
while True:
    shooter = random.choice(players)
    target = random.choice([p for p in players if p != shooter])
    hit_message = f"{shooter}:{target}"

    print("transmitting to game:", hit_message)
    UDPSocketSend.sendto(hit_message.encode(), (game_ip, send_port))

    received_data, address = UDPServerSocketReceive.recvfrom(bufferSize)
    print("received from game:", received_data.decode())
    time.sleep(2)


