import subprocess
import SplashScreen

def run_udp_socket():
    subprocess.run(["python3", "udpSocket.py"])

def run_udp_server():
    subprocess.run(["python3", "udpServer.py"])

def run_udp_client():
    subprocess.run(["python3", "udpClient.py"])

def main():
    # Show the splash screen
    SplashScreen.show_splash_screen()

    # Run the UDP socket script
    run_udp_socket()

    # Run the UDP server script
    run_udp_server()

    # Run the UDP client script
    run_udp_client()

if __name__ == "__main__":
    main()
