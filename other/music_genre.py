
import essentia
import essentia.standard as es

# Graph imports
from pylab import plot, show, figure, imshow
import matplotlib.pyplot as plt

import wave
import contextlib
import io
import base64
from pydub import AudioSegment

# Define a function to calculate the average energy of an audio file
def compute_average_energy(audio_file_path :str) -> float:
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

    '''
    # Load the audio file
    loader = es.MonoLoader(filename=audio_file_path)
    audio = loader()

    # Compute the energy of each frame in the audio
    energy_calculator = es.Energy()
    energies = [energy_calculator(frame) for frame in es.FrameGenerator(audio, frameSize=1024, hopSize=512)]

    # Calculate the average energy across all frames
    average_energy = sum(energies) / len(energies)

    return average_energy

def plot_x_second_sample(audio_file_path :str,start :int, end :int) -> None:
    '''
    Inputs:
    Outputs:

    Description:
    Using matplotlib plot the audio file as a graph for a given range
    of seconds (start to end).

    TODO: Improve graphing to more customizable format
    '''
    if end < start:
        return
    # Load the audio file
    loader = es.MonoLoader(filename=audio_file_path)
    audio = loader()

    plt.rcParams['figure.figsize'] = (15, 6) # set plot sizes to something larger than default

    plot(audio[start*44100:end*44100])
    plt.title(f"This is how the seconds {start} to {end}  of this audio looks like:")
    show()


def get_audio_file_length(audio_file_path :str) -> float:
    '''
    Inputs: audio file path (string)
    Output: duration of file in seconds (float)

    Descriiption:
    Take an audio file and return its length in seconds
    HOW: the frame rate of the file is how many frames there are
    per second == sample rate

    if we divide the number of frames by this value we can get the
    duration in seconds

    '''
    with contextlib.closing(wave.open(audio_file_path,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration


def get_sample_rate(audio_file_path):
    with contextlib.closing(wave.open(audio_file_path,'r')) as f:
        rate = f.getframerate()
    return float(rate)

def genre_predict(audio_file_path):
    s_rate = get_sample_rate(audio_file_path)
    audio = es.MonoLoader(filename=audio_file_path, sampleRate=s_rate, resampleQuality=4)()
    embedding_model = es.TensorflowPredictEffnetDiscogs(graphFilename="discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)

    model = es.TensorflowPredict2D(graphFilename="genre_discogs400-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
    predictions = model(embeddings)
    # Every frame should produce 400 nums -> search doc to see how to interpret 
    # TODO: good to map indexes to genre, think dominant genrex
    return predictions




# --- Mon 20th

'''
Got RIFF id not present proabbly beacuse tried to base64 encode the file, WHT IS RIFF?
Swtiching to pydub becasue the issue is coming from wave module - WHY SWITCH
'''

def get_audio_file_length_from_bytes(audio_bytes: bytes) -> float:
    """
    Inputs: audio file bytes (base64-decoded content)
    Output: duration of file in seconds (float)

    Description:
    Take audio file bytes and return its length in seconds.
    The frame rate of the file is how many frames there are
    per second (sample rate). Dividing the number of frames by
    this value gives the duration in seconds.
    """
    audio = io.BytesIO(audio_bytes)

    # Load the audio file into pydub
    audio = AudioSegment.from_file(audio, format="mp3")

    # Return the duration in seconds - pydub returns it in ms
    return len(audio) / 1000.0 


def get_file(file_path):
    with open(file_path, 'rb') as file:
            audio_bytes = file.read()
    
    return audio_bytes




# ----- Run functions -----

audio_file_path = '9353__guitarz1970__tinsing-1 copy.mp3'
# avg_energy = compute_average_energy(audio_file_path)
# print(f"Average Energy: {avg_energy}")

audio_bytes = get_file(audio_file_path)
duration = get_audio_file_length_from_bytes(audio_bytes)
print(f'Audio file is {duration} seconds long')

# print('predicting:')
# predictions = genre_predict(audio_file_path)
# print('done')

# plot_x_second_sample(audio_file_path,1,2)