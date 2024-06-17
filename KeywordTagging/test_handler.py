import unittest
from unittest.mock import patch, MagicMock
import json
from handler import app
from handler import process_job_description, tagDict

class HandlerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global app
        cls.app = app.test_client()
        cls.app.testing = True

    def post_job_description(self, description):
            return self.app.post('/', data=json.dumps({'description': description}),
                                content_type='application/json')
    
    def test_handler_success(self):
        test_data = {
            'description': '<p>We are looking for a full-time Python developer. Salary: $60000 - $80000 per year. Must be fluent in Spanish.</p>'
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('salary', response_data)
        self.assertIn('ES', response_data['group_to_keyword_dict']['languages'])
        self.assertIn('fullTime', response_data['group_to_keyword_dict']['jobType'])
        self.assertEqual(response_data['group_to_keyword_dict']['payPeriod'], 'yearly')
        self.assertEqual(response_data['group_to_keyword_dict']['salary']['min'], 60000)
        self.assertEqual(response_data['group_to_keyword_dict']['salary']['max'], 80000)

    def test_handler_no_description(self):
            test_data = {'description': ''}
            response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertIn('No job description provided', response.data.decode('utf-8'))

    def test_handler_missing_description_key(self):
            test_data = {}
            response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertIn('No data provided', response.data.decode('utf-8'))

    def test_handler_detect_languages_and_skills(self):
        test_data = {
            'description': '<p>Looking for a Python developer. Must be fluent in French and Spanish. Offering flexible work hours and bonuses.</p>'
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('FR', response_data['group_to_keyword_dict']['languages'])
        self.assertIn('ES', response_data['group_to_keyword_dict']['languages'])
        self.assertIn('flexible', response_data['group_to_keyword_dict']['workShift'])
        self.assertIn('bonus', response_data['group_to_keyword_dict']['benefits'])

    def test_handler_salary_info(self):
            test_data = {
                'description': '<p>We offer a competitive salary of $50000 to $70000 per year for the right candidate. Part-time positions are also available.</p>'
            }

            response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response_data = response.get_json()
            self.assertIn('salary', response_data)
            self.assertIn('payType', response_data['group_to_keyword_dict'])
            self.assertEqual(response_data['group_to_keyword_dict']['salary']['min'], 50000)
            self.assertEqual(response_data['group_to_keyword_dict']['salary']['max'], 70000)
            self.assertIn('partTime', response_data['group_to_keyword_dict']['jobType'])

    @patch('handler.fasttext.load_model')
    def test_english_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__en'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': '<p>This is a job description written in English.</p>'
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('EN', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_spanish_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__es'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description':"<p>Esta es una descripción de trabajo escrita en español.</p>"
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('ES', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_french_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__fr'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "<p>Ceci est une description de travail écrite en français.</p>"
            }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('FR', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_chinese_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__zh'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': '<p>这是一份用中文写的工作描述。</p>'
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('ZH', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_hindi_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__hi'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': '<p>यह अंग्रेजी में लिखा गया नौकरी विवरण है।</p>'
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('HI', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_arabic_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__ar'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "<p>هذه وصف وظيفة مكتوب باللغة العربية.</p>"
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('AR', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_portuguese_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__pt'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "<p>Esta é uma descrição de trabalho escrita em português.</p>"
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('PT', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_bengali_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__bn'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "<p>এটি বাংলায় লেখা একটি কাজের বর্ণনা।</p>"
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('BN', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_russian_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__ru'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "<p>Это описание работы написано на русском языке.</p>"
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('RU', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_urdu_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__ur'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "<p>یہ انگریزی میں لکھا گیا ملازمت کا بیان ہے۔</p>"
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('UR', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_korean_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__ko'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "이것은 한국어로 작성된 직무 설명입니다."
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('KO', response_data['group_to_keyword_dict']['languages'])

    @patch('handler.fasttext.load_model')
    def test_japanese_language_detection(self, mock_load_model):
        mock_model = MagicMock()
        mock_model.predict.return_value = (['__label__ja'], [0.99])
        mock_load_model.return_value = mock_model
        
        test_data = {
            'description': "これは日本語で書かれた仕事の説明です。"
        }

        response = self.app.post('/', data=json.dumps(test_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('group_to_keyword_dict', response_data)
        self.assertIn('JA', response_data['group_to_keyword_dict']['languages'])

    def test_full_time_python_developer(self):
        test_data = {
            'description': '<p>We are looking for a full-time Python developer with health and dental benefits. Salary: $60000 - $80000 per year. Must be fluent in Spanish.</p>'
        }
        expected_output = {
            'jobType': ['fullTime'],
            'benefits': ['health', 'dental'],
            'languages': ['ES'],
            'salary': {'min': 60000, 'max': 80000},
            'payPeriod': 'yearly'
        }
        self.check_job_description(test_data, expected_output)

    def test_part_time_graphic_designer(self):
        test_data = {
            'description': '<p>We are hiring a part-time graphic designer for evening shifts. This is a contract position. Salary: $20 - $25 per hour.</p>'
        }
        expected_output = {
            'jobType': ['partTime', 'contract'],
            'workShift': ['eveningShift'],
            'salary': {'min': 20, 'max': 25},
            'payPeriod': 'hourly'
        }
        self.check_job_description(test_data, expected_output)

    def test_remote_internship(self):
        test_data = {
            'description': '<p>We have an exciting remote internship opportunity available. Must have strong communication skills. No salary.</p>'
        }
        expected_output = {
            'jobType': ['internship'],
            'workplace': ['remote'],
            'skills': ['Communication'],
            'payPeriod': 'none'
        }
        self.check_job_description(test_data, expected_output)

    def test_weekend_volunteer(self):
        test_data = {
            'description': '<p>We are seeking volunteers for weekend shifts. This is an unpaid position.</p>'
        }
        expected_output = {
            'jobType': ['volunteer'],
            'workShift': ['weekend'],
            'payPeriod': 'none'
        }
        self.check_job_description(test_data, expected_output)

    def test_hybrid_software_engineer(self):
        test_data = {
            'description': '<p>We are looking for a hybrid software engineer with bonuses and employee discounts. Must be fluent in English and Chinese.</p>'
        }
        expected_output = {
            'jobType': ['fullTime'],  # Assuming full-time as default if not specified otherwise
            'workplace': ['hybrid'],
            'benefits': ['bonus', 'employeeDiscounts'],
            'languages': ['EN', 'ZH'],
            'payPeriod': 'none'
        }
        self.check_job_description(test_data, expected_output)

    def check_job_description(self, test_data, expected_output):
        response_data = process_job_description(test_data['description'])
        self.assertEqual(response_data['group_to_keyword_dict'], expected_output)

if __name__ == '__main__':
    unittest.main()