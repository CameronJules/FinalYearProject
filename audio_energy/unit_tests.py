import unittest
from unittest.mock import patch
import json
from lambda_function import lambda_handler, compute_average_energy

class TestAudioEnergy(unittest.TestCase):

    # --- Testing For Compute Average Energy Function ---
    def test_compute_average_energy(self):
        ''' Test with a valid audio file'''

        file = 'tinsing.mp3'
        expected_output = 0.6480382863947269

        with open(f'../music_files/{file}', 'rb') as audio_file:
            audio = audio_file.read()
            output = compute_average_energy(audio)

        self.assertEqual(output, expected_output)

    
    def test_compute_average_energy_empty_bytes(self):
        ''' Test with no audio bytes'''

        expected_output = 'audio_bytes must not be empty'

        with self.assertRaises(AssertionError) as assertion:
            compute_average_energy(b'')

        self.assertEqual(str(assertion.exception),expected_output)

    def test_compute_average_energy_non_bytes(self):
        '''Test with non-byte input'''

        expected_output = "audio_bytes must be of type bytes"

        with self.assertRaises(AssertionError) as assertion:
            compute_average_energy("Not a byte input")

        self.assertEqual(str(assertion.exception), expected_output)

    # --- Testing For Lambda Handler ---
    def test_valid_payload(self):
        '''Test output on a valid payload'''

        expected_outputs = {
            'statusCode': 200,
            'body': '{"audio file average energy": 0.6480382863947269}'
        }

        with open('../general_testing/mp3_api_gateway.json') as f:
            payload = json.load(f)
        
        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], expected_outputs['statusCode'])
        self.assertEqual(response['body'], expected_outputs['body'])

    def test_body_exists(self):
        '''Test no body in payload'''

        expected_output = {
            'statusCode' : 400,
            'body': "Missing body in request"
        }
        with open('../general_testing/no_body_payload.json') as f:
            payload = json.load(f)

        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], expected_output['statusCode'])
        self.assertIn(expected_output['body'], response['body'])

    def test_body_encoding_flag(self):
        '''Test header value for valid base64 encoding of body'''

        expected_output = {
            'statusCode' : 422,
            'body' : '{"error": "Audio file must be in base64 encoding"}'
        }

        with open('../general_testing/incorrect_encoding_payload.json') as f:
            payload = json.load(f)

        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], expected_output['statusCode'])
        self.assertIn(expected_output['body'],response['body'])

    def test_body_encoding(self):
        '''Test body for valid base64 encoding'''

        expected_output = {
            'statusCode' : 500,
            'body' : "error, decoding or duration function failed"
        }

        with open('../general_testing/incorrect_encoding_payload.json') as f:
            payload = json.load(f)
            # Add the flag for correct encoding to incorrect body
            payload['isBase64Encoded'] = True

        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], expected_output['statusCode'])
        self.assertIn(expected_output['body'],response['body'])

    def test_compute_error(self):
        '''Test output when compute energy throws error'''

        expected_output = {
            'statusCode' : 500,
            'body' : "error, decoding or duration function failed"
        }

        with open('../general_testing/mp3_api_gateway.json') as f:
            payload = json.load(f)

        with patch('lambda_function.compute_average_energy', side_effect=Exception("Processing error")):
            response = lambda_handler(payload, None)
            self.assertEqual(response['statusCode'], expected_output['statusCode'])
            self.assertIn(expected_output['body'],response['body'])

        
