import json
from librosa import load as libr_load
from librosa.effects import pitch_shift as lib_pitch_shift
from pydub import AudioSegment
import io
import tempfile
import os
import soundfile as sf

'''


'''

def pitch_shift(audio_bytes, shift_amount):
    '''
    shift amount is validated outside of the function to enable call back from api -> look into if this is correct way
    Shift the pitch of an audio file by a specified shift_amount/rate
    defualt is 12 bins per octave
    '''

    # Create mp3 audio
    audio_bytes = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_bytes, format="mp3")
    number_of_channels = audio.channels
    sample_width = audio.sample_width
    frame_rate = audio.frame_rate

    # Use temp file to get around essentia disk only read , using wav to avoid loss from compression
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.export(temp_audio_file.name, format="wav")
    # store temp file name
    temp_file_path = temp_audio_file.name
    temp_audio_file.close()

    # load the audio with librosa
    audio_array, sample_rate = libr_load(temp_file_path, sr=frame_rate)
    # remove the temp file
    os.remove(temp_audio_file.name)

    # Pitch shift the audio
    librosa_audio = lib_pitch_shift(audio_array, sr=frame_rate, n_steps=shift_amount)

    with io.BytesIO() as buffer:
        sf.write(buffer, librosa_audio, sample_rate, format='mp3')
        mp3_bytes = buffer.getvalue()
        print(sample_rate,sample_width,number_of_channels)
    

    return mp3_bytes




# def lambda_handler(event, context):
#     pass

