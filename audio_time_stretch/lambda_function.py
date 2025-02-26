import json
import essentia.standard as es
from librosa import load as libr_load
from librosa.effects import time_stretch as lib_time_stretch
from pydub import AudioSegment
import io
import tempfile
import os
import soundfile as sf

'''
Note experience degredation in audio quality when going from mp3 to bytes and back
without applying any librosa function.

found out that this is most likely caused by the compression of the mp3 file
so in the middle process switching to wav file format instead

also found out that using tobytes rather than writing to buffer would
cause issues like not having correct metadata and encoding issue which also
as tested created issues

remeber buffer.read() reads from pointer but buffer.getvalue() returns whole buffer
seek(0) used because if passing the buffer object it will read from the set pointer position
which after writing will be the end of the file and without reset will read nothing
'''

def time_stretch(audio_bytes, stretch_amount):
    '''
    Time stretch of an audio file by a specified stretch_amount/rate
    rate > 1 then the audio is sped up
    0 < rate < 1 then the audio is slowed down
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

    # Time stretch the audio by given amount
    librosa_audio = lib_time_stretch(audio_array, rate=stretch_amount)

    with io.BytesIO() as buffer:
        sf.write(buffer, librosa_audio, sample_rate, format='mp3')
        mp3_bytes = buffer.getvalue()
        print(sample_rate,sample_width,number_of_channels)
    

    return mp3_bytes




# def lambda_handler(event, context):
#     pass

