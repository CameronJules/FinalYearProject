import json
from essentia import standard as es
import io
import tempfile
from pydub import AudioSegment
import os
import base64
import numpy as np


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


def process_instruments(predictions, n):
    '''Return top n outputs from the function'''
    output = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True)[:n])

    return output

import json
from essentia import standard as es
import io
import tempfile
from pydub import AudioSegment
import os
import base64
import numpy as np
# from audio_genre.labels import labels


'''
NOTE Version required for TensorflowPredictEffnetDiscogs is essentia-tensorflow==2.1b6.dev1177
This may also require a new python version

Using a new venv for this environment, need to adjust the python version such that the newer version of essentia can be
found when using lambda

CD into folder before runnning test?
'''

# python3.10 -m venv .venv310
# source .venv310/bin/activate  

# pip install essentia==2.1b6.dev1177


labels =  [
        "accordion",
        "acousticbassguitar",
        "acousticguitar",
        "bass",
        "beat",
        "bell",
        "bongo",
        "brass",
        "cello",
        "clarinet",
        "classicalguitar",
        "computer",
        "doublebass",
        "drummachine",
        "drums",
        "electricguitar",
        "electricpiano",
        "flute",
        "guitar",
        "harmonica",
        "harp",
        "horn",
        "keyboard",
        "oboe",
        "orchestra",
        "organ",
        "pad",
        "percussion",
        "piano",
        "pipeorgan",
        "rhodes",
        "sampler",
        "saxophone",
        "strings",
        "synthesizer",
        "trombone",
        "trumpet",
        "viola",
        "violin",
        "voice"
    ]

def get_genres(audio_bytes):
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

    model = es.TensorflowPredict2D(graphFilename="mtg_jamendo_instrument-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
    activations = model(embeddings)

    # Why do we use mean
    activations_mean = np.mean(activations, axis=0)


    out = dict(zip(labels, activations_mean.tolist()))

    return out


def process_genres(predictions, n):
    '''Return top n outputs from the function'''
    output = dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True)[:n])

    return output

def handler(event, context):
    try:
        # Check structure
        if "body" not in event:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing body in request"})
            }
        
        # Check encoding
        is_base64 = event.get("isBase64Encoded", False)
        if not is_base64:
            return {
                "statusCode": 422,
                "body": json.dumps({"error": "Audio file must be in base64 encoding"})
            }
        parameters = event.get("queryStringParameters", False)
        if not parameters:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "Missing query parameters - queryStringParameters: params_dict"})
            }
        top_n = parameters.get("top_n", False) 
        if not top_n:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "Missing query parameters (top_n)"})
            }
        try:
            top_n = int(top_n)
        except Exception as e:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "top_n parameter is not a string"})
            }
    
        # Main function code
        try:
            # Decode body
            binary_data = base64.b64decode(event["body"])
            # Run duration function
            full_output = get_instruments(binary_data)
            final_output = process_instruments(full_output,top_n)

            return {
                "statusCode": 200,
                "body": json.dumps(final_output)
            }
        # Handle exception from main function
        except Exception as e:
            print("Error:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({"error, decoding or duration function failed": str(e)})
            }

    # Catch any other exceptions
    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

