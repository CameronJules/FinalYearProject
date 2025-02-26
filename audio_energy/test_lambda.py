import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler, compute_average_energy

class TestAudioEnergy(unittest.TestCase):

    @patch("lambda_function.compute_average_energy", return_value=0.64)
    def test_body_exists(self,mock_audio_length):
        '''Test no body in payload'''

        with open('../general_testing/no_body_payload.json') as f:
            payload = json.load(f)

        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertIn('Missing body in request', response['body'])

    @patch("lambda_function.compute_average_energy", return_value=0.64)
    def test_body_encoding(self,mock_audio_length):
        '''Test valid base64'''

        with open('../general_testing/valid_test_payload.json') as f:
            valid_payload = json.load(f)

        response = lambda_handler(valid_payload, None)
        self.assertEqual(response["statusCode"], 200)
    

    def test_valid_run(self):
        '''Test valid function ouput'''

        with open('../general_testing/valid_test_payload.json') as f:
            valid_payload = json.load(f)

        response = lambda_handler(valid_payload, None)
        self.assertEqual(response["statusCode"], 200)
    
