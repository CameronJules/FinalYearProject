
# from audio_length.lambda_function import get_audio_length
from audio_energy.lambda_function import compute_average_energy
from status_check.lambda_function import get_current_time_utc
# from audio_metadata.lambda_function import get_metadata
from audio_time_stretch.lambda_function import time_stretch
from audio_pitch_shift.lambda_function import pitch_shift
from audio_genre.lambda_function import get_genres, process_genres
from audio_instrument_detection.lambda_function import get_instruments, process_instruments
from pydub.utils import mediainfo
from base64 import b64encode, b64decode
import json


from pydub.playback import play
from pydub import AudioSegment
import io
import numpy as np
import matplotlib.pyplot as plt


file = "tinsing.mp3"
audio = open(f'../music_files/{file}', 'rb').read()
# bytes_in = io.BytesIO(audio)
# song = AudioSegment.from_file(bytes_in, format='mp3')
# play(song)

# file = 'tinsing copy.mp3'
# audio = open(f'../music_files/{file}', 'rb').read()
# bytes = io.BytesIO(audio)
# song = AudioSegment.from_file(bytes, format='mp3')
# # Export trimed song 
# trim_amnt = 4
# export_song = song[:(len(song)//trim_amnt)]
# export_song.export("../music_files/tinsing-4s.mp3", format="mp3")
# # play(song)



# --- Get current time ---
curr_time = get_current_time_utc()
print(curr_time)

# --- Audio length function ---
# length = get_audio_length(audio)
# print(f'the length of the audio file is : {length}')

# --- Audio energy function ---

# energy = compute_average_energy(audio)
# print(f'The average energy of the audio file is : {energy}')


# --- Audio Metadata Function ---

# metadata = get_metadata(audio)

# print(metadata)
# metadata_pool = metadata[7]
# for d in metadata_pool.descriptorNames():
#     print(d, metadata_pool[d])


# --- Audio Time Stretch ---

# bytes = time_stretch(audio, 5)
# bytes = io.BytesIO(bytes)
# song = AudioSegment.from_file(bytes, format="mp3")
# play(song)



# --- Audio Pitch Shift ---
# print(audio[:10])
# bytes = pitch_shift(audio, 1)
# bytes = io.BytesIO(bytes)
# song = AudioSegment.from_file(bytes, format='mp3')
# play(song)

# print(dir(essentia.standard))


# --- Audio Genres ---
# predictions = get_genres(audio)
# # for k,v in predictions.items():
# #     print(f'{k}: {v}')

# out = process_genres(predictions, 5)
# for k,v in out.items():
#     print(f'{k}: {v}')


# ---  Audio Instrument Detection ---
# predictions = get_instruments(audio)
# # for k,v in predictions.items():
# #     print(f'{k}: {v}')

# out = process_instruments(predictions, 5)
# for k,v in out.items():
#     print(f'{k}:{v}')


# print(note)

# print(audio[:10])

# bytes = pitch_shift(audio, 6.0)
# print(bytes[:10])
# bytes = io.BytesIO(bytes)
# print(bytes.getvalue()[:10])
bytes = time_stretch(audio, 2)
bytes = io.BytesIO(bytes)
song = AudioSegment.from_file(bytes, format='mp3')
play(song)