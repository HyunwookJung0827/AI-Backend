import fasttext
# Path to the downloaded language identification model
lang_model_path = 'lid.176.bin'

# Load the FastText language identification model
lang_model = fasttext.load_model(lang_model_path)

# Example job description with newlines
job_description = """
Job Details: Essential Duties and Responsibilities
"""

# Remove newlines from the job description
job_description_cleaned = job_description.replace('\n', ' ')

# Predict the language of the job description
predictions = lang_model.predict(job_description_cleaned, k=1)  # k=1 returns the top prediction
language_code = predictions[0][0].replace('__label__', '')
confidence = predictions[1][0]

print(f"Predicted language: {language_code} with confidence: {confidence}")