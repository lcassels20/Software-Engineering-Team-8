import threading
import time
import tkinter as tk

import GUI            # provides display_splash_screen(root, callback) and teamRegistration()
import udpSocket      # provides transmit_equipment_code()
import udpServer      # provides run_server()
import udpClient      # provides run_client()
from database import create_players_table

def start_udp_server():
    udpServer.run_server()

def start_udp_socket():
    udpSocket.transmit_equipment_code("EQ12345")
    # Removed the call to udpSocket.receive_data() because it's not implemented.

def main():
    create_players_table()
    
    root = tk.Tk()
    root.title("Photon")
    # Set the window to full screen automatically.
    root.attributes("-fullscreen", True)
    
    # Bring the window to the front.
    root.lift()
    root.attributes("-topmost", True)
    root.after(10, lambda: root.attributes("-topmost", False))
    
    # Allow exit from full-screen mode with the Escape key.
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    
    # Override the window close protocol to cancel pending callbacks.
    def on_closing():
        if hasattr(root, "splash_after_id"):
            try:
                root.after_cancel(root.splash_after_id)
            except Exception as e:
                print("Error cancelling splash_after_id:", e)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 1. Display the splash screen; after 3 seconds, call start_registration.
    GUI.display_splash_screen(root, lambda: GUI.start_registration())
    
    # 2. Start the UDP server in a daemon thread.
    server_thread = threading.Thread(target=start_udp_server, daemon=True)
    server_thread.start()
    
    time.sleep(1)  # Give UDP server time to start
    
    # 3. Start the UDP socket functionality in another daemon thread.
    socket_thread = threading.Thread(target=start_udp_socket, daemon=True)
    socket_thread.start()
    
    # 4. Run the UDP client functionality.
    udpClient.run_client()
    
    # Wait for threads (with timeout) and then start main loop.
    server_thread.join(timeout=1)
    socket_thread.join(timeout=1)
    
    print("[Main] All tests completed.")
    root.mainloop()

if __name__ == "__main__":
    main()
