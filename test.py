
# from audio_length.lambda_function import get_audio_length
from audio_energy.lambda_function import compute_average_energy
from status_check.lambda_function import get_current_time_utc
# from audio_metadata.lambda_function import get_metadata
# from audio_time_stretch.lambda_function import time_stretch
from audio_pitch_shift.lambda_function import pitch_shift
from audio_genre.lambda_function import get_genres, process_genres
from audio_instrument_detection.lambda_function import get_instruments


from pydub.playback import play
from pydub import AudioSegment
import io

# file = '9353__guitarz1970__tinsing-1 copy.mp3'
# audio = open(f'./music_files/{file}', 'rb').read()


# Use this one - CD into the directory of the function first i.e. /audio_genre
file = '9353__guitarz1970__tinsing-1 copy.mp3'
audio = open(f'../music_files/{file}', 'rb').read()


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

# bytes = time_stretch(audio, 0.5)
# bytes = io.BytesIO(bytes)
# song = AudioSegment.from_file(bytes, format="mp3")
# play(song)

# --- Audio Pitch Shift ---
print(audio[:10])
bytes = pitch_shift(audio, -0.5)
bytes = io.BytesIO(bytes)
song = AudioSegment.from_file(bytes)
play(song)

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
# for k,v in predictions.items():
#     print(f'{k}: {v}')