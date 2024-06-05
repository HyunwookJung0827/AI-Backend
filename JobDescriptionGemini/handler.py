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
    data = request.json
    try:
        prompt = "Write me a job description according to the following metadata dictionary: " + str(data)
        response = chat_session.send_message(prompt)
        print(response.text)
        return response.text
    except Exception as e:
        return str(e)
    
if __name__ == '__main__':
    app.run(debug=True, port=3002)
