import socket
import config

# Create UDP socket for broadcasting.
broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def transmit_equipment_code(equipment_code):
    # Broadcast equipment codes to port 7500 at the configured network address.
    broadcast_socket.sendto(equipment_code.encode(), (config.NETWORK_ADDRESS, 7500))
    print(f"Transmitted equipment code '{equipment_code}' to {config.NETWORK_ADDRESS}:7500")

if __name__ == "__main__":
    transmit_equipment_code("EQ12345")

