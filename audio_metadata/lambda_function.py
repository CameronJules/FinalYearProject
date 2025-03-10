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
            metadata = get_metadata(binary_data)

            return {
                "statusCode": 200,
                "body": json.dumps({"Audio file metadata": metadata})
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


