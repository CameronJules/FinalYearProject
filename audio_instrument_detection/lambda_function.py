import json
from essentia import standard as es
import io
import tempfile
from pydub import AudioSegment
import os
import base64
import numpy as np
from audio_instrument_detection.labels import labels


def get_instruments(audio_bytes):
    '''Return the top n genres for a given audio'''
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

    # load the audio
    audio = es.MonoLoader(filename=temp_file_path, sampleRate=frame_rate, resampleQuality=4)()

    # remove the temp file
    os.remove(temp_audio_file.name)

        
    embedding_model = es.TensorflowPredictEffnetDiscogs(graphFilename="discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)

    model = es.TensorflowPredict2D(graphFilename="mtg_jamendo_instrument-discogs-effnet-1.pb")
    activations = model(embeddings)

    # Why do we use mean
    activations_mean = np.mean(activations, axis=0)


    out = dict(zip(labels, activations_mean.tolist()))

    return out


def process_instruments(predictions):
    pass

