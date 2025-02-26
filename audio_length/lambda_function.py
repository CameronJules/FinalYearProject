import base64
import io
from pydub import AudioSegment
import json


def get_audio_length(audio_bytes):
            audio_file = io.BytesIO(audio_bytes)
            audio = AudioSegment.from_file(audio_file, format="mp3")
            duration = len(audio) / 1000.0  # Convert ms to seconds

            return duration

def lambda_handler(event, context):
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
    
        # Main function code
        try:
            # Decode body
            binary_data = base64.b64decode(event["body"])
            # Run duration function
            duration = get_audio_length(binary_data)

            return {
                "statusCode": 200,
                "body": json.dumps({"Audio file length (seconds)": duration})
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


