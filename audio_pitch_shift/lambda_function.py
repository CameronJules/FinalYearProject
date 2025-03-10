import json
from librosa import load as libr_load
from librosa.effects import pitch_shift as lib_pitch_shift
from pydub import AudioSegment
import io
import tempfile
import os
import soundfile as sf
import base64
import pydub
import numpy as np


def pitch_shift(audio_bytes, shift_amount):
    '''
    shift amount is validated outside of the function to enable call back from api -> look into if this is correct way
    Shift the pitch of an audio file by a specified shift_amount/rate
    defualt is 12 bins per octave
    '''

    # Create mp3 audio
    print("\nCreating tmp audio file...")
    audio_bytes = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_bytes, format="mp3")
    number_of_channels = audio.channels
    sample_width = audio.sample_width
    frame_rate = audio.frame_rate
    # Use temp file to get around essentia disk only read
    # Using wav to avoid loss from compression
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.export(temp_audio_file.name, format="wav")
    temp_file_path = temp_audio_file.name
    temp_audio_file.close()

    print("Loading tempfile to librosa...")
    audio_array, sample_rate = libr_load(temp_file_path, sr=frame_rate)
    os.remove(temp_audio_file.name)
    print("Running librosa pitch function...")
    librosa_audio = lib_pitch_shift(audio_array, sr=frame_rate, n_steps=shift_amount)
    
    print("Creating output...")
    librosa_audio_16bit = (librosa_audio * 32767).astype(np.int16) # scaling to wav range
    wav_buffer = io.BytesIO()
    sf.write(wav_buffer, librosa_audio_16bit, sample_rate, format='wav')
    wav_buffer.seek(0)
    # Convert WAV buffer to MP3
    audio = AudioSegment.from_file(wav_buffer, format="wav")
    mp3_buffer = io.BytesIO()
    audio.export(mp3_buffer, format="mp3", bitrate="192k")
    mp3_bytes = mp3_buffer.getvalue()
    
    wav_buffer.close()
    mp3_buffer.close()

    
    print("Done\n")
    return mp3_bytes


def lambda_handler(event, context):
    try:
        # Check structure
        print("Checking structure...")
        if "body" not in event:
            return {
                "statusCode": 400,
                "body": json.dumps({"client error": "Missing body in request"})
            }
        # Check encoding
        is_base64 = event.get("isBase64Encoded", False)
        if not is_base64:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "Audio file must be in base64 encoding"})
            }
        # Extract query parameters
        print("Getting query parameters...")
        parameters = event.get("queryStringParameters", False)
        if not parameters:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "Missing query parameters - queryStringParameters: params_dict"})
            }
        shift_amount = parameters.get("shift_amount", False) 
        if not shift_amount:
            return {
                "statusCode": 422,
                "body": json.dumps({"client error": "Missing query parameters (shift_amount)"})
            }
        
        # Decode body
        print("Decoding body...")
        try:
            binary_data = base64.b64decode(event["body"])
        except Exception as e:
            print("Error - decoding:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({"Decoding Error": str(e)})
            }
        # Probably need something to validate the decoding

        # Run duration function
        print("Running pitch shift...")
        try:
            altered_audio = pitch_shift(binary_data,shift_amount)
        except Exception as e:
            print("\n Error - pitch function:", str(e))
            print(f"\n Binary data: {binary_data[:10]}")
            return {
                "statusCode": 500,
                "body": {
                    "Audio function error": str(e),
                    "first 10 bytes data" : binary_data[:10]
                    }
            }

        # Encode the output
        print("Encoding output...")
        try:
            encoded_audio = base64.b64encode(altered_audio).decode("utf-8")
        except Exception as e:
            print("Error - encoding:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({"Encoding Error": str(e)})
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "audio/mpeg"},
            "body": encoded_audio,
            "isBase64Encoded": True
        }

    # Catch any other exceptions
    except Exception as e:
        print("Error - other:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"other error": str(e)})
        }



