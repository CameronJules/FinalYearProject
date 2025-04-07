import unittest
from unittest.mock import patch
import json
from lambda_function import handler, get_instruments, process_instruments

class TestAudioGenre(unittest.TestCase):
    pass
    # --- Testing For Get Intruments Function ---
    def test_gets_valid_audio(self):
        '''Test with valid audio bytes'''

        file = 'tinsing.mp3'
        # subset of values
        expected_output = {
            'values' : {
                'accordion': 0.01419785711914301,   
                'acousticbassguitar': 0.01100076362490654,
                'acousticguitar': 0.045245107263326645,
                'bass': 0.09146095812320709,
                'beat': 0.0088141318410635,
            }
        }

        with open(f'../music_files/{file}', 'rb') as audio_file:
            audio = audio_file.read()
            output = get_instruments(audio)
        
        for instrument, expected_value in expected_output['values'].items():
            self.assertIn(instrument, output)
            self.assertAlmostEqual(output[instrument], expected_value, places=4)

    def test_get_instruments_empty_bytes(self):
        '''Test with empty audio bytes'''
        expected_output = 'audio_bytes must not be empty'

        with self.assertRaises(AssertionError) as assertion:
            get_instruments(b'')

        self.assertEqual(str(assertion.exception), expected_output)

    def test_compute_average_energy_non_bytes(self):
        '''Test with non-byte input'''

        expected_output = "audio_bytes must be of type bytes"

        with self.assertRaises(AssertionError) as assertion:
            get_instruments("Not a byte input")

        self.assertEqual(str(assertion.exception), expected_output)


    # --- Testing For Process Instruments Function ---

    def test_process_instruments(self):
        '''Test processing instruments to get top n results'''
        predictions = {
            "Instrument A": 0.5,
            "Instrument B": 0.3,
            "Instrument C": 0.2,
        }
        n = 2
        expected_output = {
            "Instrument A": 0.5,
            "Instrument B": 0.3,
        }

        output = process_instruments(predictions, n)
        self.assertEqual(output, expected_output)

    def test_process_instruments_n_greater_than_predictions(self):
        '''Test processing instruments with n > available instruments'''
        predictions = {
            "Genre A": 0.5,
        }
        n = 5
        expected_output = {
            "assertion": 'N must be less than the number of predictions',
        }

        with self.assertRaises(AssertionError) as assertion:
            process_instruments(predictions, n)

        self.assertEqual(str(assertion.exception), expected_output['assertion'])

    # --- Testing For Handler Function ---
    def test_valid_payload(self):
        '''Test output on a valid payload'''

        # è value output as \\u00e8 adjusting test - needs fix
        expected_outputs = {
            'statusCode': 200,
            'predictions': {
                "synthesizer":0.2273,
                "piano":0.1964,
                "drums":0.1238,
                "flute":0.1026,
                "electricguitar":0.0984,
            }
        }

        with open('../general_testing/mp3_api_gateway.json') as f:
            payload = json.load(f)
        
        response = handler(payload, None)
        self.assertEqual(response["statusCode"], expected_outputs['statusCode'])
        for prediction, value in expected_outputs['predictions'].items():
            self.assertIn(prediction, response['body'])
            self.assertIn(str(value), response['body'])
    
    def test_handler_missing_body(self):
        '''Test missing body in payload'''
        payload = {
            'isBase64Encoded': True,
            'queryStringParameters': {
                "top_n": 5
            }
        }

        expected_output = {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing body in request"})
        }

        response = handler(payload, None)
        self.assertEqual(response["statusCode"], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])

    def test_body_encoding_flag(self):
        '''Test invalid base64 encoding'''
        payload = {
            'body': "invalid_base64",
            'queryStringParameters': {
                "top_n": 5
            }
        }

        expected_output = {
            'statusCode': 422,
            'body': json.dumps({"error": "Audio file must be in base64 encoding"})
        }

        response = handler(payload, None)
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
                "top_n": 5
            }
        }

        response = handler(payload, None)
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

        response = handler(payload, None)
        self.assertEqual(response['statusCode'], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])

    def test_missing_top_n(self):
        '''Test for when query string params exists but no top n parameter is inside'''

        expected_output = {
            "statusCode" : 422,
            "body" : '{"client error": "Missing query parameters (top_n)"}'
        }

        with open('../general_testing/mp3_api_gateway.json') as f:
            payload = json.load(f)
            payload['queryStringParameters'].pop('top_n', None)

        response = handler(payload, None)
        self.assertEqual(response['statusCode'], expected_output['statusCode'])
        self.assertEqual(response['body'], expected_output['body'])



