import pygame
import random
import time

tracks = [
    "Track01.mp3",
    "Track02.mp3",
    "Track03.mp3",
    "Track04.mp3",
    "Track05.mp3",
    "Track06.mp3",
    "Track07.mp3",
    "Track08.mp3"
]

def play():
    selected_track = random.choice(tracks)
    print(f"Now playing: {selected_track}")

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(selected_track)
        pygame.mixer.music.play()

        # You can either wait for it to finish here, or let it play in background
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

    except Exception as e:
        print(f"Failed to play {selected_track}: {e}")




