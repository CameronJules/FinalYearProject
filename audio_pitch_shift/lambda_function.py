from json import dumps as json_dumps
from librosa import load as libr_load
from librosa.effects import pitch_shift as lib_pitch_shift
from pydub import AudioSegment
from io import BytesIO
from soundfile import write as sf_write
from soundfile import read as sf_read
from base64 import b64decode, b64encode
from numpy import int16
from time import strftime, gmtime

def log(message,type):
    """ Helper function to log messages with a timestamp. """
    print(f"{strftime('%d/%m/%Y %H:%M:%S', gmtime())} [{type}] {message}")

def pitch_shift(audio_bytes, shift_amount):
    '''
    shift amount is validated outside of the function to enable call back from api -> look into if this is correct way
    Shift the pitch of an audio file by a specified shift_amount/rate
    defualt is 12 bins per octave
    '''
    log("pitch_shift: Setting up audio data", "INFO")
    # https://python-soundfile.readthedocs.io/en/0.13.1/
    audio_buffer = BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_buffer, format="mp3")
    frame_rate = audio.frame_rate

    wav_buffer = BytesIO()
    audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)

    log("pitch_shift: Loading audio into Librosa", "INFO")
    # https://librosa.org/blog/2019/07/17/resample-on-load/
    audio_array, sample_rate = libr_load(wav_buffer, sr=None)

    log("pitch_shift: Running librosa pitch function", "INFO")
    librosa_audio = lib_pitch_shift(audio_array, sr=frame_rate, n_steps=shift_amount)
    
    log("pitch_shift: Creating output", "INFO")
    # https://stackoverflow.com/questions/13039846/what-do-the-bytes-in-a-wav-file-represent
    librosa_audio_16bit = (librosa_audio * 32767).astype(int16) # scaling to wav range
    wav_buffer = BytesIO()
    sf_write(wav_buffer, librosa_audio_16bit, frame_rate, format='wav')
    wav_buffer.seek(0)
    # Convert WAV buffer to MP3
    audio = AudioSegment.from_file(wav_buffer, format="wav")
    mp3_buffer = BytesIO()
    audio.export(mp3_buffer, format="mp3", bitrate="192k")
    mp3_bytes = mp3_buffer.getvalue()
    
    wav_buffer.close()
    mp3_buffer.close()

    log("Done\n","INFO")
    return mp3_bytes


def lambda_handler(event, context):
    try:
        # Check structure
        log("lambda_handler: Checking structure", "INFO")
        if "body" not in event:
            return {
                "statusCode": 400,
                "body": json_dumps({"client error": "Missing body in request"})
            }
        # Check encoding
        is_base64 = event.get("isBase64Encoded", False)
        if not is_base64:
            return {
                "statusCode": 422,
                "body": json_dumps({"client error": "Audio file must be in base64 encoding"})
            }
        # Extract query parameters
        log("lambda_handler: Getting query parameters", "INFO")
        parameters = event.get("queryStringParameters", False)
        if not parameters:
            return {
                "statusCode": 422,
                "body": json_dumps({"client error": "Missing query parameters - queryStringParameters: params_dict"})
            }
        shift_amount = parameters.get("shift_amount", False) 
        if not shift_amount:
            return {
                "statusCode": 422,
                "body": json_dumps({"client error": "Missing query parameters (shift_amount)"})
            }
        
        # Decode body
        log("lambda_handler: Decoding body", "INFO")
        try:
            binary_data = b64decode(event["body"])
        except Exception as e:
            log(f"lambda_handler: Base64 decoding failed: {str(e)}", "ERROR")
            return {
                "statusCode": 500,
                "body": json_dumps({"Decoding Error": str(e)})
            }
        # Probably need something to validate the decoding

        # Run duration function
        log("lambda_handler: Running pitch shift", "INFO")
        try:
            altered_audio = pitch_shift(binary_data,shift_amount)
        except Exception as e:
            log(f"lambda_handler: Pitch function failed: {str(e)}", "ERROR")
            print(f"\n Binary data: {binary_data[:10]}")
            return {
                "statusCode": 500,
                "body": {
                    "Audio function error": str(e),
                    "first 10 bytes data" : binary_data[:10]
                    }
            }

        # Encode the output
        log("lambda_handler: Encoding output", "INFO")
        try:
            encoded_audio = b64encode(altered_audio).decode("utf-8")
        except Exception as e:
            log("Handler - Error encoding:", str(e))
            return {
                "statusCode": 500,
                "body": json_dumps({"Encoding Error": str(e)})
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
            "body": json_dumps({"other error": str(e)})
        }



