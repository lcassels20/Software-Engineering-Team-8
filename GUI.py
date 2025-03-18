import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk, ImageSequence
from database import (
    insert_player, player_exists, get_player_code_name,
    get_player_count, update_equipment_id
)
import udpSocket  # Transmits equipment codes after player addition
import playerAction  # For transitioning to the player action screen
import config  # Import network configuration

# Global lists to store players added in this session.
red_players = []
green_players = []

# Global variable to hold the main Tk instance
app_root = None

def set_animated_background(parent_frame, gif_path):
    """
    Loads an animated GIF, places it behind all widgets in parent_frame,
    and continuously animates it.
    """
    frames = []
    with Image.open(gif_path) as im:
        try:
            while True:
                frame_copy = im.copy()
                frames.append(frame_copy)
                im.seek(im.tell() + 1)
        except EOFError:
            pass

    bg_label = tk.Label(parent_frame)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    tk_frames = []
    parent_frame.update_idletasks()
    width = parent_frame.winfo_width() or 640
    height = parent_frame.winfo_height() or 480
    for frame in frames:
        resized = frame.resize((width, height), Image.Resampling.LANCZOS)
        tk_frames.append(ImageTk.PhotoImage(resized))
    
    def animate(idx=0):
        bg_label.config(image=tk_frames[idx])
        parent_frame.after(100, animate, (idx + 1) % len(tk_frames))
    
    if tk_frames:
        animate(0)
    
    bg_label.lower()
    
    def on_resize(event):
        new_width = event.width
        new_height = event.height
        new_tk_frames = []
        for frame in frames:
            resized = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
            new_tk_frames.append(ImageTk.PhotoImage(resized))
        tk_frames[:] = new_tk_frames
    
    parent_frame.bind("<Configure>", on_resize)

def display_splash_screen(root, callback):
    """
    Displays 'splashbg.gif' (resized to fill the window) as the animated background.
    After 6 seconds, the splash screen is removed and 'callback()' is called.
    """
    global app_root
    app_root = root

    splash_frame = tk.Frame(root, highlightthickness=2, highlightbackground="#FFFF33")
    splash_frame.pack(fill=tk.BOTH, expand=True)

    splash_frame.update_idletasks()
    width = splash_frame.winfo_width() or root.winfo_screenwidth()
    height = splash_frame.winfo_height() or root.winfo_screenheight()

    gif_path = "splashbg.gif"
    frames = []
    try:
        pil_img = Image.open(gif_path)
        while True:
            frame_copy = pil_img.copy()
            frame_copy = frame_copy.resize((width, height), Image.Resampling.LANCZOS)
            frames.append(ImageTk.PhotoImage(frame_copy))
            pil_img.seek(len(frames))
    except EOFError:
        pass

    bg_label = tk.Label(splash_frame)
    bg_label.pack(fill=tk.BOTH, expand=True)

    def animate(index=0):
        if frames:
            bg_label.config(image=frames[index])
            splash_frame.after(100, animate, (index + 1) % len(frames))
    if frames:
        animate(0)

    def after_callback():
        if not root.winfo_exists():
            return
        splash_frame.destroy()
        callback()

    root.splash_after_id = root.after(6000, after_callback)

def start_registration():
    """
    Displays a network settings prompt on a yellow background with a yellow border
    matching the splash screen.
    """
    network_frame = tk.Frame(app_root, bg="#AB7E02", highlightthickness=2, highlightbackground="#FFFF33")
    network_frame.pack(fill=tk.BOTH, expand=True)
    
    try:
        logo_network_img_pil = Image.open("logoNetwork.png").convert("RGBA")
        logo_network_img = ImageTk.PhotoImage(logo_network_img_pil)
        logo_label = tk.Label(network_frame, image=logo_network_img, bg="#AB7E02")
        logo_label.image = logo_network_img
        logo_label.pack(pady=20)
    except Exception as e:
        print("Error loading logoNetwork.png:", e)

    default_label = tk.Label(
        network_frame,
        text=f"Default Address: {config.NETWORK_ADDRESS}",
        bg="#AB7E02",
        fg="White",
        font=("Arial", 16)
    )
    default_label.pack(pady=10)

    question_label = tk.Label(
        network_frame,
        text="Welcome to Photon",
        bg="#AB7E02",
        fg="White",
        font=("Arial", 28)
    )
    question_label.pack(pady=10)

    yes_button = tk.Button(
        network_frame,
        text="Change network",
        font=("Arial", 20),
        command=lambda: [network_frame.destroy(), show_network_selection()],
        borderwidth=0, highlightthickness=0, relief="flat",
        bg="#AB7E02", activebackground="#AB7E02", fg="white"
    )
    yes_button.pack(pady=5)

    no_button = tk.Button(
        network_frame,
        text="Play",
        font=("Arial", 20),
        command=lambda: [network_frame.destroy(), teamRegistration()],
        borderwidth=0, highlightthickness=0, relief="flat",
        bg="#AB7E02", activebackground="#AB7E02", fg="white"
    )
    no_button.pack(pady=5)

def show_network_selection():
    """
    A separate screen to select a new network address from presets.
    """
    network_settings_frame = tk.Frame(app_root, bg="#AB7E02", highlightthickness=2, highlightbackground="#FFFF33")
    network_settings_frame.pack(fill=tk.BOTH, expand=True)
    
    instruction_label = tk.Label(
        network_settings_frame,
        text="Select a new network address:",
        bg="#AB7E02",
        fg="black",
        font=("Helvetica", 16)
    )
    instruction_label.pack(pady=20)
    
    def handle_network_selection(addr):
        if addr == "custom":
            new_addr = simpledialog.askstring("Custom Network", "Enter a custom network address:", parent=network_settings_frame)
            if new_addr:
                config.NETWORK_ADDRESS = new_addr
                messagebox.showinfo("Info", f"Network address updated to {new_addr}")
            else:
                messagebox.showwarning("Warning", "No network address entered. Keeping default.")
        else:
            config.NETWORK_ADDRESS = addr
            messagebox.showinfo("Info", f"Network address updated to {addr}")
        network_settings_frame.destroy()
        teamRegistration()
    
    preset_addresses = [
        ("Custom", "custom"),
        ("Default", "127.0.0.1")
    ]
    
    for text, addr in preset_addresses:
        btn = tk.Button(
            network_settings_frame,
            text=text,
            command=lambda addr=addr: handle_network_selection(addr),
            font=("Helvetica", 14),
            borderwidth=0, highlightthickness=0, relief="flat",
            bg="#AB7E02", activebackground="#AB7E02", fg="white"
        )
        btn.pack(pady=10)
    
    cancel_btn = tk.Button(
        network_settings_frame,
        text="Cancel",
        command=lambda: [network_settings_frame.destroy(), teamRegistration()],
        font=("Helvetica", 14),
        borderwidth=0, highlightthickness=0, relief="flat",
        bg="#AB7E02", activebackground="#AB7E02", fg="white"
    )
    cancel_btn.pack(pady=10)

def countdown_screen(callback):
    """
    Displays a full-window countdown (3, 2, 1, "Game Starting") on a solid yellow background.
    The background color (#FFFF33) matches your border color. The network logo appears at the top,
    and the countdown (in Arial) is positioned towards the bottom.
    """
    # Create an overlay frame with a solid yellow background (same as border)
    countdown_frame = tk.Frame(app_root, bg="#AB7E02")
    countdown_frame.place(relwidth=1, relheight=1)
    
    # Display the network logo at the top
    try:
        logo_img_pil = Image.open("logoNetwork.png").convert("RGBA")
        logo_img = ImageTk.PhotoImage(logo_img_pil)
        logo_label = tk.Label(countdown_frame, image=logo_img, bg="#AB7E02")
        logo_label.image = logo_img
        logo_label.pack(side="top", pady=20)
    except Exception as e:
        print("Error loading logoNetwork.png for countdown:", e)
    
    # Create a countdown label positioned towards the bottom center
    countdown_label = tk.Label(countdown_frame, text="", font=("Arial", 72), fg="White", bg="#AB7E02")
    countdown_label.place(relx=0.5, rely=0.8, anchor="center")
    
    def update_count(i):
        if i > 0:
            countdown_label.config(text=str(i))
            countdown_frame.after(1000, update_count, i-1)
        else:
            countdown_label.config(text="Game Starting")
            countdown_frame.after(500, lambda: [countdown_frame.destroy(), callback()])
    
    update_count(3)

def popup_add_player(team, container):
    popup = tk.Toplevel(app_root)
    popup.title(f"Add {team} Player")
    popup.grab_set()

    team_bg = "#592020" if team == "Red" else "#20592e"
    popup.configure(bg=team_bg)

    tk.Label(popup, text="Enter Player ID (max 6 characters):", bg=team_bg, fg="#FFFF33").grid(
        row=0, column=0, padx=10, pady=10, sticky="e"
    )
    player_id_entry = tk.Entry(popup)
    player_id_entry.grid(row=0, column=1, padx=10, pady=10)
    
    def on_next():
        player_id = player_id_entry.get().strip()
        if not player_id:
            messagebox.showerror("Error", "Player ID is required.")
            return
        if len(player_id) > 6:
            messagebox.showerror("Error", "Player ID must be at most 6 characters.")
            return
        existing_code_name = get_player_code_name(player_id)
        if existing_code_name is None:
            count = get_player_count(team)
            if count >= 15:
                messagebox.showerror("Error", f"Maximum players (15) reached for {team} team.")
                return
        player_id_entry.config(state="disabled")
        next_button.destroy()
        if existing_code_name is not None:
            tk.Label(popup, text="Code Name:", bg=team_bg, fg="#FFFF33").grid(
                row=1, column=0, padx=10, pady=10, sticky="e"
            )
            code_name_var = tk.StringVar(value=existing_code_name)
            code_name_entry = tk.Entry(popup, textvariable=code_name_var, state="disabled")
            code_name_entry.grid(row=1, column=1, padx=10, pady=10)
        else:
            tk.Label(popup, text="Enter New Code Name:", bg=team_bg, fg="#FFFF33").grid(
                row=1, column=0, padx=10, pady=10, sticky="e"
            )
            code_name_entry = tk.Entry(popup)
            code_name_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(popup, text="Equipment ID (integer):", bg=team_bg, fg="#FFFF33").grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        equip_entry = tk.Entry(popup)
        equip_entry.grid(row=2, column=1, padx=10, pady=10)
        submit_button = tk.Button(
            popup,
            text="Submit",
            command=lambda: on_submit(player_id, code_name_entry, equip_entry, existing_code_name),
            borderwidth=0, highlightthickness=0, relief="flat",
            bg=team_bg, activebackground=team_bg, fg="#FFFF33"
        )
        submit_button.grid(row=3, column=0, columnspan=2, pady=10)

    next_button = tk.Button(
        popup,
        text="Next",
        command=on_next,
        borderwidth=0, highlightthickness=0, relief="flat",
        bg=team_bg, activebackground=team_bg, fg="#FFFF33"
    )
    next_button.grid(row=0, column=2, padx=10, pady=10)

    def on_submit(player_id, code_name_entry, equip_entry, existing_code_name):
        code_name = code_name_entry.get().strip()
        equip_id = equip_entry.get().strip()
        if not equip_id:
            messagebox.showerror("Error", "Equipment ID is required.")
            return
        try:
            int(equip_id)
        except ValueError:
            messagebox.showerror("Error", "Equipment ID must be an integer.")
            return
        if existing_code_name is not None:
            try:
                update_equipment_id(player_id, equip_id)
                udpSocket.transmit_equipment_code(equip_id)
            except Exception as e:
                print("Error updating player:", e)
        else:
            if not code_name:
                messagebox.showerror("Error", "Code Name is required.")
                return
            try:
                insert_player(player_id, code_name, equip_id, team)
                udpSocket.transmit_equipment_code(equip_id)
            except Exception as e:
                print("Error inserting player:", e)
        player_tuple = (player_id, code_name, equip_id, team)
        if team == "Red":
            red_players.append(player_tuple)
        else:
            green_players.append(player_tuple)
        label = tk.Label(container, text=code_name, fg="#FFFF33", font=("Arial", 14))
        label.pack(padx=10, pady=5)
        container.update_idletasks()
        popup.destroy()

def clear_all_entries(red_container, green_container):
    print("Clear All Entries triggered (Red + Green)")
    red_players.clear()
    green_players.clear()
    if red_container:
        for widget in red_container.winfo_children():
            widget.destroy()
    if green_container:
        for widget in green_container.winfo_children():
            widget.destroy()

def teamRegistration():
    registration = tk.Frame(app_root, bg="black", highlightthickness=2, highlightbackground="#FFFF33")
    registration.pack(fill=tk.BOTH, expand=True)
    
    content_frame = tk.Frame(registration, bg="black")
    content_frame.pack(fill=tk.BOTH, expand=True)
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
    
    # ------------------ RED TEAM (Left) ------------------
    redFrame = tk.Frame(content_frame, highlightthickness=2, highlightbackground="#FFFF33")
    redFrame.grid(row=0, column=0, sticky="nsew")
    redFrame.config(width=640, height=480)
    redFrame.pack_propagate(False)
    
    set_animated_background(redFrame, "redprg.gif")
    
    red_player_container = tk.Frame(redFrame, bd=0)
    red_player_container.place(relx=0.5, rely=0.5, anchor="center")
    
    # Create a Button sized to the PNG image for "Add Player"
    try:
        add_red_img_pil = Image.open("addPlayer.png").convert("RGBA")
        add_red_img = ImageTk.PhotoImage(add_red_img_pil)
    except Exception as e:
        print("Error loading addPlayer.png:", e)
        add_red_img = None

    add_red_button = tk.Button(
        redFrame,
        image=add_red_img,
        command=lambda: popup_add_player("Red", red_player_container),
        borderwidth=0,
        highlightthickness=0,
        relief=tk.FLAT,
        width=add_red_img.width(),
        height=add_red_img.height()
    )
    add_red_button.place(relx=0.2, rely=0.9, anchor="center")
    add_red_button.image = add_red_img

    # "Submit Players" button for Red
    try:
        submitRed_img_pil = Image.open("submitPlayers.png").convert("RGBA")
        submitRed_img = ImageTk.PhotoImage(submitRed_img_pil)
    except Exception as e:
        print("Error loading submitPlayers.png:", e)
        submitRed_img = None

    submit_red_button = tk.Button(
        redFrame,
        image=submitRed_img,
        command=lambda: print("Red team submission (players stored in session)"),
        borderwidth=0,
        highlightthickness=0,
        relief=tk.FLAT,
        width=submitRed_img.width(),
        height=submitRed_img.height()
    )
    submit_red_button.place(relx=0.5, rely=0.9, anchor="center")
    submit_red_button.image = submitRed_img

    # "Clear All" button for Red
    try:
        clear_all_img_pil = Image.open("clearEntries.png").convert("RGBA")
        clear_all_img = ImageTk.PhotoImage(clear_all_img_pil)
    except Exception as e:
        print("Error loading clearEntries.png:", e)
        clear_all_img = None

    clear_all_button = tk.Button(
        redFrame,
        image=clear_all_img,
        command=lambda: clear_all_entries(red_player_container, green_player_container),
        borderwidth=0,
        highlightthickness=0,
        relief=tk.FLAT,
        width=clear_all_img.width(),
        height=clear_all_img.height()
    )
    clear_all_button.place(relx=0.8, rely=0.9, anchor="center")
    clear_all_button.image = clear_all_img

    # ------------------ GREEN TEAM (Right) ------------------
    greenFrame = tk.Frame(content_frame, highlightthickness=2, highlightbackground="#FFFF33")
    greenFrame.grid(row=0, column=1, sticky="nsew")
    greenFrame.config(width=640, height=480)
    greenFrame.pack_propagate(False)
    
    set_animated_background(greenFrame, "greenrpg.gif")
    
    green_player_container = tk.Frame(greenFrame, bd=0)
    green_player_container.place(relx=0.5, rely=0.5, anchor="center")

    # "Start Game" button for Green
    try:
        start_img_pil = Image.open("startGame.png").convert("RGBA")
        start_img = ImageTk.PhotoImage(start_img_pil)
    except Exception as e:
        print("Error loading startGame.png:", e)
        start_img = None

    start_game_button = tk.Button(
        greenFrame,
        image=start_img,
        # Instead of directly starting the game, call countdown_screen first.
        command=lambda: countdown_screen(lambda: playerAction.start_game(app_root, players=red_players + green_players)),
        borderwidth=0,
        highlightthickness=0,
        relief=tk.FLAT,
        width=start_img.width(),
        height=start_img.height()
    )
    start_game_button.place(relx=0.2, rely=0.9, anchor="center")
    start_game_button.image = start_img

    # "Submit Players" button for Green
    try:
        submitGreen_img_pil = Image.open("submitPlayers.png").convert("RGBA")
        submitGreen_img = ImageTk.PhotoImage(submitGreen_img_pil)
    except Exception as e:
        print("Error loading submitPlayers.png:", e)
        submitGreen_img = None

    submit_green_button = tk.Button(
        greenFrame,
        image=submitGreen_img,
        command=lambda: print("Green team submission (players stored in session)"),
        borderwidth=0,
        highlightthickness=0,
        relief=tk.FLAT,
        width=submitGreen_img.width(),
        height=submitGreen_img.height()
    )
    submit_green_button.place(relx=0.5, rely=0.9, anchor="center")
    submit_green_button.image = submitGreen_img

    # "Add Player" button for Green
    try:
        add_green_img_pil = Image.open("addPlayer.png").convert("RGBA")
        add_green_img = ImageTk.PhotoImage(add_green_img_pil)
    except Exception as e:
        print("Error loading addPlayer.png:", e)
        add_green_img = None

    add_green_button = tk.Button(
        greenFrame,
        image=add_green_img,
        command=lambda: popup_add_player("Green", green_player_container),
        borderwidth=0,
        highlightthickness=0,
        relief=tk.FLAT,
        width=add_green_img.width(),
        height=add_green_img.height()
    )
    add_green_button.place(relx=0.8, rely=0.9, anchor="center")
    add_green_button.image = add_green_img
