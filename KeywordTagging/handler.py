from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import json

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

# Skip reinstalling the required layer
DetectorFactory.seed = 0

# Set to use to detect when to catch a word for tagging
wordStopperSet = {' ', '.', ',', '(', ')', '{', '}', '[', ']', '-', '!', '/', ':', ';', '&', '+', '<', '>'}
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

# Dictionary to search the matching keyword from the job description
tagDict = {
    'full': ['jobType', 'fullTime'],
    'fulltime': ['jobType', 'fullTime'],
    'part': ['jobType', 'partTime'],
    'parttime': ['jobType', 'partTime'],
    'contract': ['jobType', 'contract'],
    'intern': ['jobType', 'internship'],
    'internship': ['jobType', 'internship'],
    'commission': ['jobType', 'commission'],
    'volunteer': ['jobType', 'volunteer'],
    'weekend': ['workShift', 'weekend'],
    'weekends': ['workShift', 'weekend'],
    'evening': ['workShift', 'eveningShift'],
    'night': ['workShift', 'nightShift'],
    'flexible': ['workShift', 'flexible'],
    'health': ['benefits', 'health'],
    'dental': ['benefits', 'dental'],
    'vision': ['benefits', 'vision'],
    'life': ['benefits', 'life'],
    'bonus': ['benefits', 'bonus'],
    '401k': ['benefits', '_401k'],
    'commuter': ['benefits', 'commuter'],
    'discount': ['benefits', 'employeeDiscounts'],
    'discounts': ['benefits', 'employeeDiscounts'],
    'referral': ['benefits', 'referral'],
    'spanish': ['languages', 'ES'],
    'communication': ['skills', 'Communication'],
    'teamwork': ['skills', 'Teamwork'],
    'leadership': ['skills', 'Leadership'],
    'adaptability': ['skills', 'Adaptability'],
    'site': ['workplace', 'onSite'],
    'remote': ['workplace', 'remote'],
    'hybrid': ['workplace', 'hybrid']
    }
    
@app.route('/', methods=['POST'])
@cross_origin()  # allow all origins all methods.
def handler():
    data = request.json
    jobDescription = data.get('description', '')

    if not jobDescription:
        return jsonify({'error': 'No job description provided'}), 400

    try:
        # detectedLanguages: Set of detected languages (unprocessed)
        detectedLanguages = set()
        # detectedKeyword: Set of detected keywords 
        detectedKeyword = set()
        
        # ex: { 'employmentType': ['full', 'part', 'hybrid']}
        groupToKeywordDict = {}
        
        # beginningOfSentence: index where the last sentence ends in jobDescription
        beginningOfSentence = 0
        # beginningOfWord: index where the last word ends in jobDescription
        beginningOfWord = 0
        groupToKeywordDict['languages'] = set()

        for jobDescriptionIndex, char in enumerate(jobDescription):
            if char in sentenceStopperSet and beginningOfSentence < jobDescriptionIndex:
                # Detect language for each sentence
                sentence = jobDescription[beginningOfSentence: jobDescriptionIndex].strip()
                if len(sentence) > 7:  # Skip empty sentences
                    lang = detect(sentence)
                    detectedLanguages.add(lang)
                # Update beginningOfSentence
                beginningOfSentence = jobDescriptionIndex + 1
            
        # Filter the detected language set to only have top 12 languages for immigrants
        detectedLanguages = [lang.upper() for lang in detectedLanguages if lang in topLanguageSet]
        
        if 'EN' in detectedLanguages:
            for jobDescriptionIndex, char in enumerate(jobDescription):
                if char in wordStopperSet and beginningOfWord < jobDescriptionIndex:
                    word = jobDescription[beginningOfWord: jobDescriptionIndex].strip().lower()
                    if word in tagDict:
                        group = tagDict[word][0]
                        # Example: (word: tagDict[word][0]) is ('full': 'employmentType')
                        # Inside groupToKeywordDict, we want to store
                        # { 'employmentType': ['full', 'part', 'hybrid']}
                        if group in groupToKeywordDict:
                            groupToKeywordDict[group].add(word)
                        else:
                            groupToKeywordDict[group] = {word}
                        
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
        
    except LangDetectException as e:
        return jsonify({'error': f'Language detection failed: {str(e)}'}), 400

    return jsonify({
        'detected_languages': detectedLanguages,
        'group_to_keyword_dict': groupToKeywordDict
    }), 200
if __name__ == '__main__':
    app.run(debug=True, port=3001)
