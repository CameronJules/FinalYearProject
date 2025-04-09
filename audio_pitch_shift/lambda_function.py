from json import dumps as json_dumps
from pydub import AudioSegment
from io import BytesIO
from base64 import b64decode, b64encode
from time import strftime, gmtime
import numpy as np

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

def speedx(sound_array, factor):
    """ Multiplies the sound's speed by some `factor` """
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[ indices.astype(int) ]

def stretch(sound_array, f, window_size, h):
    """ 
    Stretches the sound by a factor `f`
    https://zulko.github.io/blog/2014/03/29/soundstretching-and-pitch-shifting-in-python/

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

def stretch_stereo(sound_array, f, window_size, h):
    if len(sound_array.shape) == 1:
        # Mono audio
        return stretch(sound_array, f, window_size, h)
    
    # Stereo audio
    left_channel = stretch(sound_array[:, 0], f, window_size, h)
    right_channel = stretch(sound_array[:, 1], f, window_size, h)
    
    # Combine the two channels back into stereo
    return np.column_stack((left_channel, right_channel))

def np_pitchshift(snd_array, n, window_size=2**13, h=2**11):
    """ Changes the pitch of a sound by ``n`` semitones. """
    factor = 2**(1.0 * n / 12.0)
    
    stretched = stretch(snd_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)

def pitch_shift(audio_bytes, shift_amount):
    assert audio_bytes, "audio_bytes must not be empty"
    assert isinstance(audio_bytes, bytes), "audio_bytes must be of type bytes"
    assert isinstance(shift_amount, float), "shift_amount must be of type float"
    '''
    shift pitch by n semitones
    https://batulaiko.medium.com/how-to-pitch-shift-in-python-c59b53a84b6d
    '''
    log("pitch_shift: Writing audio to buffer", "INFO")
    audio_buffer = BytesIO(audio_bytes)
    fr, y = read(audio_buffer)

    log("Shifting Pitch", "INFO")
    if y.ndim == 2:
        # Stereo audio
        y_hat = np.column_stack([
            np_pitchshift(y[:, 0], shift_amount),
            np_pitchshift(y[:, 1], shift_amount)
        ])
    else:
        # Mono audio
        y_hat = np_pitchshift(y, shift_amount)

    log("Pitch Shift: Writing Output", "INFO")
    output_buffer = BytesIO()
    write(output_buffer, fr, y_hat)

    output_buffer.seek(0)
    
    log("Pitch Shift: Success\n", "INFO")
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
                "body": json_dumps({"error, decoding or duration function failed": str(e)})
            }
        # Probably need something to validate the decoding

        # Run duration function
        try:
            shift_amount = float(shift_amount)
        except Exception as e:
            return {
                "statusCode": 422,
                "body": {
                    "Shift amount invalid": str(e),}
            }
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



