from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
import fasttext
from tags import tagDict

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

# Path to the downloaded language identification model
lang_model_path = 'lid.176.bin'

try:
    # Load the FastText language identification model
    lang_model = fasttext.load_model(lang_model_path)
except Exception as e:
    raise RuntimeError(f"Failed to load language model: {str(e)}")

# Set to use to detect when to catch a word for tagging
wordStopperSet = {' ', '(', ')', '{', '}', '[', ']', '-', '/', ':', ';', '&', '+', '<', '>'}
# Set to use to detect some unnecessary ends of a word. Newly added for salary info processing
unnecessaryEndsSet = {'.', ',', '(', ')', '{', '}', '[', ']', '-', '!', '/', ':', ';', '&', '+', '<', '>'}
# Set to use to detect when to catch a sentence for language detection
sentenceStopperSet = {'.', '!', '。', '<', '>'}

# Detectable (immigrants-friendly) language Set 
"""
English (en)
Spanish (es)
French (fr)
Chinese (Mandarin) (zh)
Hindi (hi)
Arabic (ar)
Portuguese (pt)
Bengali (bn)
Russian (ru)
Urdu (ur)
Korean (ko)
Japanese (ja)
"""
topLanguageSet = {'en', 'es', 'fr', 'zh', 'hi', 'ar', 'pt', 'bn', 'ru', 'ur', 'ko', 'ja'}


@app.route('/', methods=['POST'])
@cross_origin()  # allow all origins all methods.
def handler():
    data = request.json
    if not data:
            return jsonify({'error': 'No data provided'}), 400
        
    jobDescription = data.get('description', '')
    if not jobDescription:
        return jsonify({'error': 'No job description provided'}), 400

    try:
        # detectedLanguages: Set of detected languages (unprocessed)
        detectedLanguages = set()
        
        # ex: { 'employmentType': ['full', 'part', 'hybrid']}
        groupToKeywordDict = {}
        
        # beginningOfSentence: index where the last sentence ends in jobDescription
        beginningOfSentence = 0
        # beginningOfWord: index where the last word ends in jobDescription
        beginningOfWord = 0
        groupToKeywordDict['languages'] = set()
        salaryList = []
        skipping = False

        for jobDescriptionIndex, char in enumerate(jobDescription):
            # Don't process anything inside the tag
            if char == '>':
                skipping = False
                beginningOfSentence = jobDescriptionIndex + 1
            elif skipping:
                continue
            elif char in sentenceStopperSet and beginningOfSentence < jobDescriptionIndex or jobDescriptionIndex == len(jobDescription) - 1:
                if char == '<':
                    skipping = True
                # Detect language for each sentence
                sentence = jobDescription[beginningOfSentence: jobDescriptionIndex].strip()
                while sentence and sentence[-1] in unnecessaryEndsSet:
                        sentence = sentence[:-1]
                while sentence and sentence[0] in unnecessaryEndsSet:
                    sentence = sentence[1:]
                if len(sentence) >= 10:  # Skip empty sentences
                    # Predict the language of the job description
                    predictions = lang_model.predict(sentence, k=1)  # k=1 returns the top prediction
                    lang = predictions[0][0].replace('__label__', '')
                    confidence = predictions[1][0]
                    #print(lang, confidence, sentence)
                    if confidence > 0.8:
                        detectedLanguages.add(lang)
                # Update beginningOfSentence
                beginningOfSentence = jobDescriptionIndex + 1
            
        # Filter the detected language set to only have top 12 languages for immigrants
        detectedLanguages = [lang.upper() for lang in detectedLanguages if lang in topLanguageSet]
        
        if 'EN' in detectedLanguages:
            for jobDescriptionIndex, char in enumerate(jobDescription):
                if char in wordStopperSet and beginningOfWord < jobDescriptionIndex or jobDescriptionIndex == len(jobDescription) - 1:
                    # Process each word in lowercase
                    word = jobDescription[beginningOfWord: jobDescriptionIndex].strip().lower()
                    while word and word[-1] in unnecessaryEndsSet:
                        word = word[:-1]
                    while word and word[0] in unnecessaryEndsSet:
                        word = word[1:]
                    if word:
                        if word in tagDict:
                            group = tagDict[word][0]
                            # Example: (word: tagDict[word][0]) is ('full': 'employmentType')
                            # Inside groupToKeywordDict, we want to store
                            # { 'employmentType': ['full', 'part', 'hybrid']}
                            if group in groupToKeywordDict:
                                groupToKeywordDict[group].add(word)
                            else:
                                groupToKeywordDict[group] = {word}
                        elif word[0] == "$":
                            # Process the salary info when $ is detected and there are less than 2 salary info
                            # If there are more than 2 salary info, the rest are probably tips or too complicated to process 
                            word = word[1:].replace(',', '')
                            wordIndex = 0
                            while wordIndex < len(word) and word[wordIndex].isdigit():
                                wordIndex += 1
                            salaryList.append(word[:wordIndex])

                        
                    # Update beginningOfWord
                    beginningOfWord = jobDescriptionIndex + 1
                
        # Before putting into JSON
        # Translate each keyword to the matching keyword in our database
        for group in groupToKeywordDict:
            # group ex: 'employmentType'
            # groupToKeywordDict[group] ex: ['full', 'part', 'hybrid']
            # key ex: 'full', 'part', 'hybrid'
            groupToKeywordDict[group] = [tagDict[key][1] for key in list(groupToKeywordDict[group])]

        groupToKeywordDict['languages'] += [lang for lang in detectedLanguages if lang not in groupToKeywordDict['languages']]
        
        # Process the salary info
        if salaryList:
            # Sort the salaryList to get the max and min salary
            salaryList = sorted(salaryList)
            if len(salaryList) == 1:
                groupToKeywordDict['payType'] = 'minimum'
                groupToKeywordDict['salary'] = {'max': int(salaryList[0]), 'min': int(salaryList[0])}
            else:
                # If there are more than 1 salary info, it is a range
                # It cannot be zero because we already checked if there is any salary info
                groupToKeywordDict['payType'] = 'range'
                # The last element is the max salary and the second to last element is the min salary
                # The rest of smaller salary info are probably tips
                groupToKeywordDict['salary'] = {'max': int(salaryList[-1]), 'min': int(salaryList[-2]) if len(salaryList[-1]) - len(salaryList[-2]) <= 1 else int(salaryList[-1])}
                # print(groupToKeywordDict['salary'])

            if len(str(groupToKeywordDict['salary']['max'])) <= 3:
                # If the salary is hourly, it is less than $1000
                groupToKeywordDict['payPeriod'] = 'hourly'
            else:
                # $1,000 ~ $999,999 and over is yearly
                groupToKeywordDict['payPeriod'] = 'yearly'

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 400

    return jsonify({
        'group_to_keyword_dict': groupToKeywordDict,
        'salary': salaryList
    }), 200

if __name__ == '__main__':
    try:
        app.run(debug=True, port=3001)
    except Exception as e:
        raise RuntimeError(f"Failed to start the application: {str(e)}")