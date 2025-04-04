import json
from essentia import standard as es
import io
import tempfile
from pydub import AudioSegment
import os
import base64

# Define a function to calculate the average energy of an audio file
def compute_average_energy(audio_bytes) -> float:
    '''
    Input: audio file path (string)
    Output: average energy (float)

    Description:
    We use essentia Energy function to calculate the energy in specific
    frames of audio, we store the energy of each frame in an array and
    then calculate the average.
    A frame is a fixed length window from the audio file.

    NOTE: 44,100 samples/second == 44,100 Hz == 44.1kHz
    When we take a frame of 1024 this is 1024/44,100 seconds assuming audio
    has a sample rate of 44.1kHz

    hop size is how much each frame is overlayed on top of the previous frame

    Essentia can only read from file, for api we need data to be read from the body
    variable which will be binary so we create a temp file to allow read.

    '''
    assert audio_bytes, "audio_bytes must not be empty"
    assert isinstance(audio_bytes, bytes), "audio_bytes must be of type bytes"

    # Create mp3 audio
    audio_bytes = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_bytes, format="mp3")
    # Use temp file to get around essentia disk only read
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_audio_file:
        audio.export(temp_audio_file.name, format="mp3")
        # store temp file name
        temp_file_path = temp_audio_file.name
 
        # load the audio
        loader = es.MonoLoader(filename=temp_file_path)
        audio = loader()


    # Compute the energy of each frame in the audio
    energy_calculator = es.Energy()
    energies = [energy_calculator(frame) for frame in es.FrameGenerator(audio, frameSize=1024, hopSize=1024)]

    # Calculate the average energy across all frames
    average_energy = sum(energies) / len(energies)

    return average_energy


def lambda_handler(event, context):
    try:
        # Check structure
        if "body" not in event:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing body in request"})
            }
        
        # Check encoding flag
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
            energy = compute_average_energy(binary_data)

            return {
                "statusCode": 200,
                "body": json.dumps({'audio file average energy': energy})
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


