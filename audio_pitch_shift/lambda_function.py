from json import dumps as json_dumps
from pydub import AudioSegment
from io import BytesIO
from base64 import b64decode, b64encode
from time import strftime, gmtime

def log(message,type):
    """ Helper function to log messages with a timestamp. """
    print(f"{strftime('%d/%m/%Y %H:%M:%S', gmtime())} [{type}] {message}")

def pitch_shift(audio_bytes, shift_amount):
    '''
    shift amount in ocatves
    https://batulaiko.medium.com/how-to-pitch-shift-in-python-c59b53a84b6d
    '''
    log("pitch_shift: Writing audio to buffer", "INFO")
    audio_buffer = BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_buffer, format="mp3")

    log("pitch_shift: Adjusting sample rate", "INFO")
    new_sample_rate = int(audio.frame_rate * (2.0 ** shift_amount))

    log("pitch_shift: Applying audio shift", "INFO")
    pitch_shifted_sound = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
    pitch_shifted_sound = pitch_shifted_sound.set_frame_rate(44100)

    log("pitch_shift: Writing output", "INFO")
    mp3_buffer = BytesIO()
    pitch_shifted_sound.export(mp3_buffer, format="mp3")
    mp3_bytes = mp3_buffer.getvalue()
    mp3_buffer.close()
    
    log("Success\n", "INFO")
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
            shift_amount = float(shift_amount)
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



