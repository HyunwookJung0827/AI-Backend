"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import google.generativeai as genai
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError("API key missing")

# Configure the generative AI library with the API key
genai.configure(api_key=api_key)

app = Flask(__name__)

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 2000, #8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[]
)
@app.route('/', methods=['POST'])
@cross_origin()  # allow all origins all methods.
def handler():
    try:
        data = request.json['values']
        # print(data)
        if '_id' in data:
            del data['_id']
        if 'description' in data:
            del data['description']
        if 'industryId' in data:
            del data['industryId']
        if 'companyLocationId' in data:
            del data['companyLocationId']
        if 'isExactLocation' in data:
            del data['isExactLocation']
        if 'hireTerm' in data:
            del data['hireTerm']
        for key in list(data):
            if not data[key]:
                del data[key]
        if 'experienceLevel' in data and 'isExperienceRequired' in data:
            del data['isExperienceRequired']
        # print(data)
        prompt = "Write me a job description in rich text format according to the following metadata dictionary. Do not include the job title or how-to-apply section. Do not use ** or #. Instead, if you want to style it, use tag such as <h1> or <strong>. Make sure every text is covered in tag like <p>. Here's the rest of metadata from the user:"  + str(data)
        response = chat_session.send_message(prompt)
        if not response.text or response.text[0] != '<' or response.text[-1] != '>':
            response.text = "<p>" + response.text + "</p>"
        # print(type(response.text))
        return response.text
    except KeyError as e:
        return f"KeyError: {str(e)}", 400
    except ValueError as e:
        return str(e), 500
    except Exception as e:
        return str(e), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=3002)
