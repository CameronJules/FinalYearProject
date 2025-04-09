import unittest
from unittest.mock import patch
import json
from lambda_function import handler, get_genres, process_genres

class TestAudioGenre(unittest.TestCase):
    # --- Testing For Get Genres Function ---
    def test_get_genres_valid_audio(self):
        '''Test with valid audio bytes'''

        file = 'tinsing.mp3'
        # subset of values
        expected_output = {
            'values' : {
                'Blues---Boogie Woogie': 0.00026125568547286093,
                'Blues---Chicago Blues': 0.0005003822734579444,
                'Blues---Country Blues': 0.0007937308982945979,
                'Blues---Delta Blues': 0.0008477121591567993
            }
        }

        with open(f'../music_files/{file}', 'rb') as audio_file:
            audio = audio_file.read()
            output = get_genres(audio)
        
        for genre_value, expected_value in expected_output['values'].items():
            self.assertIn(genre_value, output)
            self.assertAlmostEqual(output[genre_value], expected_value, places=4)

    def test_get_genres_empty_bytes(self):
        '''Test with empty audio bytes'''
        expected_output = 'audio_bytes must not be empty'

        with self.assertRaises(AssertionError) as assertion:
            get_genres(b'')

        self.assertEqual(str(assertion.exception), expected_output)

    def test_compute_average_energy_non_bytes(self):
        '''Test with non-byte input'''

        expected_output = "audio_bytes must be of type bytes"

        with self.assertRaises(AssertionError) as assertion:
            get_genres("Not a byte input")

        self.assertEqual(str(assertion.exception), expected_output)


    # --- Testing For Process Genres Function ---

    def test_process_genres(self):
        '''Test processing genres to get top n results'''
        predictions = {
            "Genre A": 0.5,
            "Genre B": 0.3,
            "Genre C": 0.2,
        }
        n = 2
        expected_output = {
            "Genre A": 0.5,
            "Genre B": 0.3,
        }

        output = process_genres(predictions, n)
        self.assertEqual(output, expected_output)

    def test_process_genres_n_greater_than_predictions(self):
        '''Test processing genres with n > available genres'''
        predictions = {
            "Genre A": 0.5,
        }
        n = 5
        expected_output = {
            "assertion": 'N must be less than the number of predictions',
        }

        with self.assertRaises(AssertionError) as assertion:
            process_genres(predictions, n)

        self.assertEqual(str(assertion.exception), expected_output['assertion'])

    # --- Testing For Handler Function ---
    def test_valid_payload(self):
        '''Test output on a valid payload'''

        # è value output as \\u00e8 adjusting test - needs fix
        expected_outputs = {
            'statusCode': 200,
            'predictions': {
                "Electronic---Experimental": 0.2462,
                "Electronic---Ambient": 0.1935,
                "Electronic---Dungeon Synth": 0.0978,
                "Electronic---Musique Concr\\u00e8te": 0.0741,
                "Stage & Screen---Soundtrack": 0.0663,
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



