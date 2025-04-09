from json import dumps as json_dumps
from pydub import AudioSegment
from base64 import b64decode, b64encode
import numpy as np
from time import strftime, gmtime
from io import BytesIO

'''
Note experience degredation in audio quality when going from mp3 to bytes and back
without applying any librosa function.

found out that this is most likely caused by the compression of the mp3 file
so in the middle process switching to wav file format instead

also found out that using tobytes rather than writing to buffer would
cause issues like not having correct metadata and encoding issue which also
as tested created issues

remeber buffer.read() reads from pointer but buffer.getvalue() returns whole buffer
seek(0) used because if passing the buffer object it will read from the set pointer position
which after writing will be the end of the file and without reset will read nothing
'''

def read(audio_buffer, normalized=False):
    """MP3 to numpy array - https://stackoverflow.com/questions/53633177/how-to-read-a-mp3-audio-file-into-a-numpy-array-save-a-numpy-array-to-mp3"""
    a = AudioSegment.from_file(audio_buffer, format="mp3")
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y
    
def write(f, sr, x, normalized=False):
    """numpy array to MP3"""
    channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
    if normalized:  # normalized array - each item should be a float in [-1, 1)
        y = np.int16(x * 2 ** 15)
    else:
        y = np.int16(x)
    song = AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
    song.export(f, format="mp3", bitrate="320k")
    
def log(message,type):
    """ Helper function to log messages with a timestamp. """
    print(f"{strftime('%d/%m/%Y %H:%M:%S', gmtime())} [{type}] {message}")

def stretch(sound_array, f, window_size, h):
    """ 
    Stretches the sound by a factor `f`
    https://zulko.github.io/blog/2014/03/29/soundstretching-and-pitch-stretching-in-python/

    """
    if len(sound_array.shape) == 2:  # Stereo signal
        sound_array = sound_array.mean(axis=1).astype('int16')  # Convert to mono

    phase  = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(int(len(sound_array) / f + window_size))  # Cast to int

    for i in np.arange(0, len(sound_array)-(window_size+h), h*f):
        a1 = sound_array[int(i): int(i) + window_size]
        a2 = sound_array[int(i) + h: int(i) + window_size + h]


        s1 =  np.fft.fft(hanning_window * a1)
        s2 =  np.fft.fft(hanning_window * a2)
        phase = (phase + np.angle(s2/s1)) % (2*np.pi)  # Corrected modulo
        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))

        i2 = int(i/f)
        result[i2 : i2 + window_size] += (hanning_window * a2_rephased.real)

    result = ((2**(16-4)) * result/result.max())
    return result.astype('int16')


def time_stretch(audio_bytes, stretch_amount):
    '''
    Time stretch of an audio file by a specified stretch_amount/rate
    rate > 1 then the audio is sped up
    0 < rate < 1 then the audio is slowed down
    '''
    # Create mp3 audio
    audio_bytes = BytesIO(audio_bytes)
    fr, y = read(audio_bytes)

    y_hat = stretch(y, stretch_amount, window_size=2**13, h=2**11)

    output_buffer = BytesIO()
    write(output_buffer, fr, y_hat)

    output_buffer.seek(0)

    
    return output_buffer.getvalue()




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
        stretch_amount = parameters.get("stretch_amount", False) 
        if not stretch_amount:
            return {
                "statusCode": 422,
                "body": json_dumps({"client error": "Missing query parameters (stretch_amount)"})
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
        try:
            stretch_amount = float(stretch_amount)
        except Exception as e:
            return {
                "statusCode": 422,
                "body": {
                    "Stretch amount invalid": str(e),}
            }

        # Run duration function
        log("lambda_handler: Running time stretch", "INFO")
        try:
            altered_audio = time_stretch(binary_data,stretch_amount)
        except Exception as e:
            log(f"lambda_handler: Stretch function failed: {str(e)}", "ERROR")
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
