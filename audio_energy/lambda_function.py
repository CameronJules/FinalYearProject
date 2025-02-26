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
    loader = es.MonoLoader(filename=temp_file_path)
    audio = loader()
    # remove the temp file
    os.remove(temp_audio_file.name)

    # Compute the energy of each frame in the audio
    energy_calculator = es.Energy()
    energies = [energy_calculator(frame) for frame in es.FrameGenerator(audio, frameSize=1024, hopSize=1024)]

    # Calculate the average energy across all frames
    average_energy = sum(energies) / len(energies)

    return average_energy

def lambda_handler(event, context):
    is_base64 = event.get("isBase64Encoded", False)

    # Check structure
    if "body" not in event:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing body in request"})
        }
    

    # Decode if necessary
    if is_base64:
        binary_data = base64.b64decode(event["body"])
    else:
        # TODO: What is latin1: 
        binary_data = event["body"].encode("latin1")  # Raw binary data

    try:
        energy = compute_average_energy(binary_data)
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid audio data.", "details": str(e)}),
        }



    return {
        'statusCode': 200,
        'body' : json.dumps({'audio file average energy': energy})
    }