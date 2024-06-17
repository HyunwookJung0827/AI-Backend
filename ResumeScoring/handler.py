import yake
import requests
import fitz  # PyMuPDF
import json

# Set to use to detect when to catch a word for tagging
wordStopperSet = {' ', '(', ')', '{', '}', '[', ']', '-', '/', ':', ';', '&', '+', '<', '>'}
# Set to use to detect some unnecessary ends of a word. Newly added for salary info processing
unnecessaryEndsSet = {'.', ',', '(', ')', '{', '}', '[', ']', '-', '!', '/', ':', ';', '&', '+', '<', '>'}

NUMBER_OF_KEYWORDS = 20 # Number of keywords to extract
N = 1 # Number of words each keyword can contain

def fetch_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception("Failed to fetch the PDF")

def parse_pdf(pdf_content):
    with fitz.open(stream=pdf_content, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def extract_resume_data(text):
    # Example: Extracting sections based on keywords
    lines = text.split('\n')
    name = None
    contact_info = []
    skills = []
    
    for line in lines:
        if "Name" in line:
            name = line.split(':')[1].strip()
        elif "Email" in line or "Phone" in line:
            contact_info.append(line.strip())
        elif "Skills" in line:
            skills_line_index = lines.index(line) + 1
            skills = lines[skills_line_index].strip().split(', ')
    
    resume_data = {
        'name': name,
        'contact_info': contact_info,
        'skills': skills
    }
    
    return resume_data

def structure_data(resume_data):
    return json.dumps(resume_data, indent=2)

url = "https://cdn.workonward.com/bfd60054-85e7-4c4a-ac01-81e2f10feec3.pdf"
pdf_content = fetch_pdf(url)
text = parse_pdf(pdf_content)
resume_data = extract_resume_data(text)
structured_resume = structure_data(resume_data)

print(pdf_content)
print(text)
print(resume_data)
print(structured_resume)

def extract_keywords(text, language="en", deduplication_threshold=0.9, num_of_keywords=NUMBER_OF_KEYWORDS):
    kw_extractor = yake.KeywordExtractor(lan=language, n=N, dedupLim=deduplication_threshold, top=num_of_keywords, features=None)
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]

def score_resume(parsed_data, job_description):
    resumeText = parsed_data
    beginningOfWord = 0
    jobKeywords = {keyword.lower(): False for keyword in extract_keywords(job_description)}
    for resumeTextIndex, char in enumerate(resumeText):
        if char in wordStopperSet and beginningOfWord < resumeTextIndex or resumeTextIndex == len(resumeText) - 1:
            # Process each word in lowercase
            word = resumeText[beginningOfWord: resumeTextIndex].strip().lower()
            while word and word[-1] in unnecessaryEndsSet:
                word = word[:-1]
            while word and word[0] in unnecessaryEndsSet:
                word = word[1:]
            if word and word in jobKeywords:
                if word in jobKeywords:
                    jobKeywords[word] = True
            # Update beginningOfWord
            beginningOfWord = resumeTextIndex + 1

    print(f"Job Keywords: {jobKeywords}", len(jobKeywords))
    score = 0
    for keyword in jobKeywords:
        if jobKeywords[keyword]:
            score += (100/NUMBER_OF_KEYWORDS)
    print(f"Score: {int(score)}", score)
    score = int(score)
    # resumeText = ' '.join([parsed_data.get('summary', ''), ' '.join(parsed_data.get('skills', []))])
    # resume_keywords = extract_keywords(resumeText)
    # jobKeywords = extract_keywords(job_description)

    # matched_keywords = set(resume_keywords).intersection(set(jobKeywords))
    # unmatched_keywords = set(resume_keywords).difference(set(jobKeywords))
    # print(f"Resume Keywords: {resume_keywords}", len(resume_keywords))
    # print(f"Job Keywords: {jobKeywords}", len(jobKeywords))
    # print(f"Matched Keywords: {matched_keywords}", len(matched_keywords))
    # print(f"Unmatched Keywords: {unmatched_keywords}", len(matched_keywords))
    # score = (len(matched_keywords) / len(jobKeywords)) * 100 if jobKeywords else 0

    return score

# Example usage
resume_parsed_data = {
    'summary': 'Seasoned software developer with over 7 years of experience in Python, JavaScript, and cloud technologies. Adept at developing scalable applications and working with cross-functional teams to deliver high-quality software solutions.',
    'skills': [
        'Python', 'JavaScript', 'Django', 'Flask', 'React', 'AWS', 'Azure', 'Google Cloud', 
        'microservices', 'Docker', 'Kubernetes', 'machine learning', 'data analysis', 'Git', 'CI/CD', 'Agile'
    ],
    'experience': [
        {
            'job_title': 'Senior Software Developer',
            'company': 'Tech Innovators Inc.',
            'duration': '3 years',
            'responsibilities': 'Led a team of developers to build and maintain web applications using Python, Django, and React. Implemented CI/CD pipelines and deployed applications on AWS.'
        },
        {
            'job_title': 'Software Developer',
            'company': 'Cloud Solutions Ltd.',
            'duration': '4 years',
            'responsibilities': 'Developed and maintained software solutions using Flask and Angular. Worked with cloud platforms such as Azure and Google Cloud. Participated in Agile development processes and code reviews.'
        }
    ],
    'education': [
        {
            'degree': 'Bachelor of Science in Computer Science',
            'institution': 'University of Technology',
            'year': '2014'
        }
    ],
    'certifications': [
        'AWS Certified Solutions Architect',
        'Certified Kubernetes Administrator'
    ]
}
resume_parsed_data = text

job_description = """
We are seeking a highly skilled and experienced Senior Software Developer to join our dynamic team. 
The ideal candidate will have extensive experience in developing and maintaining software applications using Python, JavaScript, and cloud technologies. 
Key responsibilities include:
- Designing, developing, and implementing software applications that meet business needs.
- Collaborating with cross-functional teams to define, design, and ship new features.
- Troubleshooting, debugging, and upgrading existing software.
- Ensuring the performance, quality, and responsiveness of applications.
- Maintaining code quality, organization, and automation.

Requirements:
- Bachelor's degree in Computer Science, Information Technology, or related field.
- 5+ years of professional experience in software development.
- Proficiency in Python, JavaScript, and experience with frameworks such as Django, Flask, React, or Angular.
- Experience with cloud platforms such as AWS, Azure, or Google Cloud.
- Strong understanding of software development methodologies, version control (Git), and CI/CD pipelines.
- Excellent problem-solving skills and attention to detail.
- Strong communication and teamwork skills.

Preferred Qualifications:
- Master's degree in Computer Science or related field.
- Experience with microservices architecture and containerization (Docker, Kubernetes).
- Knowledge of machine learning and data analysis.
- Familiarity with Agile development processes.
- Certifications in relevant technologies.

We offer a competitive salary, comprehensive benefits package, and opportunities for professional growth and development. If you are passionate about software development and eager to work in a fast-paced, innovative environment, we encourage you to apply.
"""


score = score_resume(resume_parsed_data, job_description)
print(f"Resume Score: {score}")