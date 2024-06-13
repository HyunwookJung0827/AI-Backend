import unittest
from unittest.mock import patch, MagicMock
import json
from handler import app

class HandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('handler.chat_session.send_message')
    def test_handler_success(self, mock_send_message):
        # Arrange
        test_data = {
            'values': {
                'experienceLevel': 'Mid',
                'skills': 'Python, Flask',
                'location': 'Remote'
            }
        }
        response_text = "<p>This is a job description.</p>"
        mock_send_message.return_value = MagicMock(text=response_text)

        # Act
        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        # simulates a POST request to the Flask app with test_data as the payload.

        # Assert
        self.assertEqual(response.status_code, 200)
        # This checks if the HTTP status code of the response is 200, which means the request was successful.
        self.assertIn(response_text, response.data.decode('utf-8'))
        # This checks if the response_text is part of the actual response body.

    @patch('handler.chat_session.send_message')
    def test_handler_missing_values_key(self, mock_send_message):
        # Arrange
        test_data = {}
        mock_send_message.return_value = MagicMock(text="")

        # Act
        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("KeyError", response.data.decode('utf-8'))

    @patch('handler.chat_session.send_message')
    def test_handler_with_empty_fields(self, mock_send_message):
        # Arrange
        test_data = {
            'values': {
                'experienceLevel': 'Mid',
                'skills': '',
                'location': None
            }
        }
        response_text = "<p>This is a job description.</p>"
        mock_send_message.return_value = MagicMock(text=response_text)

        # Act
        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(response_text, response.data.decode('utf-8'))
    
    @patch('handler.chat_session.send_message')
    def test_handler_html_wrapping(self, mock_send_message):
        # Arrange
        test_data = {
            'values': {
                'experienceLevel': 'Mid',
                'skills': 'Python, Flask',
                'location': 'Remote'
            }
        }
        response_text = "This is a job description."
        mock_send_message.return_value = MagicMock(text=response_text)

        # Act
        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("<p>" + response_text + "</p>", response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
