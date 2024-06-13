import yake

def extract_keywords(text, language="en", deduplication_threshold=0.9, num_of_keywords=20):
    kw_extractor = yake.KeywordExtractor(lan=language, n=2, dedupLim=deduplication_threshold, top=num_of_keywords, features=None)
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]

def score_resume(parsed_data, job_description):
    resume_text = ' '.join([parsed_data.get('summary', ''), ' '.join(parsed_data.get('skills', []))])
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matched_keywords = set(resume_keywords).intersection(set(job_keywords))
    print(f"Resume Keywords: {resume_keywords}", len(resume_keywords))
    print(f"Job Keywords: {job_keywords}", len(job_keywords))
    print(f"Matched Keywords: {matched_keywords}", len(matched_keywords))
    score = (len(matched_keywords) / len(job_keywords)) * 100 if job_keywords else 0

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