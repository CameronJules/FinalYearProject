import unittest
from unittest.mock import patch
import json
from lambda_function import lambda_handler, pitch_shift, read, write
import numpy as np
from io import BytesIO

class TestPitchShift(unittest.TestCase):
    
    # --- Test for pitch shift ---

    def test_pitch_shift_up(self):
        ''' Test pitch shifts up by correct amount - one semitone'''
        # Genereate sample wave in numpy
        duration = 5
        rate = 44100
        frequency = 440 # A note
        semitones = 1.0
        expected_freq = frequency * 2 ** (semitones / 12)

        t = np.linspace(0, duration, int(rate * duration)) # Time dimension of samples
        wave = np.sin(2 * np.pi * frequency * t) # Create the sin wave for 440
        normalized_wave = (wave * 32767).astype(np.int16) # Convert to audio range
        
        # Convert the wave to byte sample
        audio_buffer = BytesIO()
        write(audio_buffer, 44100, normalized_wave)
        mp3_bytes = audio_buffer.getvalue()

        # Shift the sample wave to a known new pitch
        output_bytes = pitch_shift(mp3_bytes, semitones)
        sr, shifted_wave = read(BytesIO(output_bytes))

        # Extract the new frequency with FFT
        # https://dsp.stackexchange.com/questions/78355/how-to-extract-the-dominant-frequency-from-the-audio-wav-file-using-numpy
        fft_data = np.fft.fft(shifted_wave)
        freqs = np.fft.fftfreq(len(shifted_wave))
    
        peak_coefficient = np.argmax(np.abs(fft_data))
        peak_freq = freqs[peak_coefficient]
        output_frequency = abs(peak_freq * rate)

        # Check the changed req and the expected match or are close
        self.assertAlmostEqual(output_frequency, expected_freq, delta=1) # difference of +- 1


    # --- Test for lambda lambda_handler ---

    def test_valid_run(self):
        '''Test valid run'''
        expected_output = {
            'statusCode' : 200
        }
        with open("../general_testing/mp3_api_gateway.json", 'r') as file:
            payload = json.load(file)

        response = lambda_handler(payload,None)

        self.assertEqual(response['statusCode'],expected_output['statusCode'])
    
    def test_invalid_shift(self):
        '''Test for invalid shift input'''
        expected_output = {
            'statusCode' : 422,
            'body' : 'Shift amount invalid'
        }

        with open("../general_testing/mp3_api_gateway.json", 'r') as file:
            payload = json.load(file)
            payload['queryStringParameters']['shift_amount'] = "invalid_value"

        response = lambda_handler(payload,None)

        self.assertEqual(response['statusCode'],expected_output['statusCode'])
        self.assertIn(expected_output['body'],response['body'])



    def test_lambda_handler_missing_body(self):
        '''Test missing body in payload'''
        payload = {
            'isBase64Encoded': True,
            'queryStringParameters': {
                "shift_amount": 5
            }
        }

        expected_output = {
            "statusCode": 400,
            "body": '{"client error": "Missing body in request"}'
        }

        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])

    def test_body_encoding_flag(self):
        '''Test invalid base64 encoding'''
        payload = {
            'body': "invalid_base64",
            'queryStringParameters': {
                "shift_amount": 5
            }
        }

        expected_output = {
            'statusCode': 422,
            'body': json.dumps({"client error": "Audio file must be in base64 encoding"})
        }

        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])

    def test_body_encoding(self):
        '''Test body for valid base64 encoding'''

        expected_output = {
            'statusCode' : 500,
            'body' : "error, decoding or duration function failed"
        }

        payload = {
            'body' : "Not base64",
            'isBase64Encoded' : True,
            "queryStringParameters": {
                "shift_amount": 5
            }
        }

        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], expected_output['statusCode'])
        self.assertIn(expected_output['body'],response['body'])

    def test_missing_query_parameters(self):
        '''Test for query parameters'''

        expected_output = {
            "statusCode" : 422,
            "body" : '{"client error": "Missing query parameters - queryStringParameters: params_dict"}'
        }

        with open('../general_testing/mp3_api_gateway.json') as f:
            payload = json.load(f)
            payload.pop('queryStringParameters', None)

        response = lambda_handler(payload, None)
        self.assertEqual(response['statusCode'], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])

    def test_missing_shift_amount(self):
        '''Test for when query string params exists but no shift_amount parameter is inside'''

        expected_output = {
            "statusCode" : 422,
            "body" : '{"client error": "Missing query parameters (shift_amount)"}'
        }

        with open('../general_testing/mp3_api_gateway.json') as f:
            payload = json.load(f)
            payload['queryStringParameters'].pop('shift_amount', None)

        response = lambda_handler(payload, None)
        self.assertEqual(response['statusCode'], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])


