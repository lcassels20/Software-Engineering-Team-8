from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
import gametrack as gt
import random
import time

tracks = [
    "Track1.mp3",
    "Track2.mp3",
    "Track3.mp3",
    "Track4.mp3",
    "Track5.mp3",
    "Track6.mp3",
    "Track7.mp3",
    "Track8.mp3"
]

def randomMusic(__init__):
    return
    
def play():
    selected_track = random.choice(tracks)
    print(f"Now playing: {selected_track}")
    
    # Load and play the audio
    audio = AudioSegment.from_file(selected_track)
    play_obj = _play_with_simpleaudio(audio)
    
    # Wait until playback is finished
    play_obj.wait_done()
