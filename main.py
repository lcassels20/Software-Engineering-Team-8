import database
import threading
import time
import tkinter as tk

import GUI            # provides display_splash_screen(root, callback) and teamRegistration()
import udpSocket      # provides transmit_equipment_code()
import udpServer      # provides run_server()
import udpClient      # provides run_client()

def main():
    # Drop the old players table to avoid schema conflicts.
    #database.clear_players_table()
    # Create a fresh table with the updated schema.
    database.create_players_table()
    
    # Rest of your main() code...
    root = tk.Tk()
    root.title("Photon")
    root.attributes("-fullscreen", True)
    root.lift()
    root.attributes("-topmost", True)
    root.after(10, lambda: root.attributes("-topmost", False))
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    
    def on_closing():
        if hasattr(root, "splash_after_id"):
            try:
                root.after_cancel(root.splash_after_id)
            except Exception as e:
                print("Error cancelling splash_after_id:", e)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    GUI.display_splash_screen(root, lambda: GUI.start_registration())
    
    server_thread = threading.Thread(target=udpServer.run_server, daemon=True)
    server_thread.start()
    
    time.sleep(1)  # Give UDP server time to start
    
    socket_thread = threading.Thread(target=udpSocket.transmit_equipment_code, args=("EQ12345",), daemon=True)
    socket_thread.start()
    
    udpClient.run_client()
    
    server_thread.join(timeout=1)
    socket_thread.join(timeout=1)
    
    print("[Main] All tests completed.")
    root.mainloop()

if __name__ == "__main__":
    main()
