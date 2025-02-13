import socket

# Create a UDP socket for broadcasting
broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Create a UDP socket for receiving
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_socket.bind(('127.0.0.1', 7501))

def transmit_equipment_code(equipment_code):
    # Send equipment code to all players
    broadcast_socket.sendto(equipment_code.encode(), ('127.0.0.1', 7501))

def receive_data():
    # Receive data from players
    data, addr = receive_socket.recvfrom(1024)
    return data.decode(), addr

# Example usage
if __name__ == "__main__":
    # Transmit equipment code after player addition
    transmit_equipment_code("EQ12345")
    
    # Receive data from players
    data, addr = receive_data()
    print(f"Received data: {data} from {addr}")
