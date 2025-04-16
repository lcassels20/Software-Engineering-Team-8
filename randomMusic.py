from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
import random

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
        audio = AudioSegment.from_file(selected_track)
        play_obj = _play_with_simpleaudio(audio)
        play_obj.wait_done()
    except Exception as e:
        print(f"Failed to play {selected_track}: {e}")



