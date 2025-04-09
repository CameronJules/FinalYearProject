import unittest
from unittest.mock import patch
import json
from lambda_function import lambda_handler, time_stretch, read, write
import numpy as np
from io import BytesIO

class TestTimeStretch(unittest.TestCase):
    
    # --- Test for pitch shift ---

    def test_time_stretch(self):

        # Create sample wave
        duration = 5
        rate = 44100
        frequency = 440 # A note
        stretch_factor = 1.5
        expected_output = {
            'frequency' : frequency,
            'duration' : duration/stretch_factor
        }

        t = np.linspace(0, duration, int(rate * duration)) # Time dimension of samples
        wave = np.sin(2 * np.pi * frequency * t) # Create the sin wave for 440
        normalized_wave = (wave * 32767).astype(np.int16) # Convert to audio range
        
        # Convert the wave to byte sample
        audio_buffer = BytesIO()
        write(audio_buffer, 44100, normalized_wave)
        mp3_bytes = audio_buffer.getvalue()

        # Time stretch
        output_bytes = time_stretch(mp3_bytes, stretch_factor)
        sr, stretched_wave = read(BytesIO(output_bytes))

        # Check the duration is expected
        output_duration = len(stretched_wave)/sr

        # Check the pitch is the same
        fft_data = np.fft.fft(stretched_wave)
        freqs = np.fft.fftfreq(len(stretched_wave))
    
        peak_coefficient = np.argmax(np.abs(fft_data))
        peak_freq = freqs[peak_coefficient]
        output_frequency = abs(peak_freq * rate)

        self.assertAlmostEqual(output_duration, expected_output['duration'],delta=1)
        self.assertAlmostEqual(output_frequency, expected_output['frequency'], delta=1)

    # --- Test for lambda function ---

    def test_valid_run(self):
        '''Test valid run'''
        expected_output = {
            'statusCode' : 200
        }
        with open("../general_testing/mp3_api_gateway.json", 'r') as file:
            payload = json.load(file)

        response = lambda_handler(payload,None)

        self.assertEqual(response['statusCode'],expected_output['statusCode'])
    
    def test_invalid_stretch(self):
        '''Test for invalid stretch factor'''
        expected_output = {
            'statusCode' : 422,
            'body' : 'Stretch amount invalid'
        }

        with open("../general_testing/mp3_api_gateway.json", 'r') as file:
            payload = json.load(file)
            payload['queryStringParameters']['stretch_amount'] = "invalid_value"

        response = lambda_handler(payload,None)

        self.assertEqual(response['statusCode'],expected_output['statusCode'])
        self.assertIn(expected_output['body'],response['body'])



    def test_lambda_handler_missing_body(self):
        '''Test missing body in payload'''
        payload = {
            'isBase64Encoded': True,
            'queryStringParameters': {
                "stretch_amount": 1.5
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
                "stretch_amount": 1.5
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
            'body' : "Decoding Error"
        }

        payload = {
            'body' : "Not base64",
            'isBase64Encoded' : True,
            "queryStringParameters": {
                "stretch_amount": 1.5
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

    def test_missing_stretch_amount(self):
        '''Test for when query string params exists but no shift_amount parameter is inside'''

        expected_output = {
            "statusCode" : 422,
            "body" : '{"client error": "Missing query parameters (stretch_amount)"}'
        }

        with open('../general_testing/mp3_api_gateway.json') as f:
            payload = json.load(f)
            payload['queryStringParameters'].pop('stretch_amount', None)

        response = lambda_handler(payload, None)
        self.assertEqual(response['statusCode'], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])
