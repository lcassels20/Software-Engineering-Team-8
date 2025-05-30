import database
import threading
import time
import tkinter as tk

import GUI            # provides display_splash_screen(root, callback) and teamRegistration()
import udpSocket      # provides transmit_equipment_code()
import udpClient      # provides run_client()

def main():
    database.create_players_table()

    root = tk.Tk()
    root.title("Photon")
    root.attributes("-fullscreen", True)
    root.lift()
    root.attributes("-topmost", True)
    root.after(10, lambda: root.attributes("-topmost", False))
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    after_ids = []
    
    def on_closing():
        # Cancel splash screen delay if still scheduled
        if hasattr(root, "splash_after_id"):
            try:
                root.after_cancel(root.splash_after_id)
                print("Splash screen timer cancelled.")
            except Exception as e:
                print("Error cancelling splash_after_id:", e)

        # Cancel any additional tracked after() timers
        for aid in after_ids:
            try:
                root.after_cancel(aid)
            except Exception as e:
                print(f"Failed to cancel timer {aid}:", e)

        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    def after_splash():
        # Start background socket broadcasts and client after splash screen is gone
        threading.Thread(target=udpSocket.transmit_equipment_code, args=("EQ12345",), daemon=True).start()
        threading.Thread(target=udpClient.run_client, daemon=True).start()
        GUI.start_registration()

    GUI.display_splash_screen(root, after_splash)

    root.mainloop()

if __name__ == "__main__":
    main()






