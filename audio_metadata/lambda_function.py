import json
from essentia import standard as es
import io
import tempfile
from pydub import AudioSegment
import os
import base64


def get_metadata(audio_bytes):
    '''
    Given an mpeg format file return the metadata stored in the
    file.

    '''
    # Create mp3 audio
    audio_bytes = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_bytes, format="mp3")
    # Use temp file to get around essentia disk only read
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    audio.export(temp_audio_file.name, format="mp3")
    # store temp file name
    temp_file_path = temp_audio_file.name
    temp_audio_file.close()

    # load the audio

    metadata = es.MetadataReader(filename=temp_file_path, failOnError=True)()

    os.remove(temp_audio_file.name)

    return metadata