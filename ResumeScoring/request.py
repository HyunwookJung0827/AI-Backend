import requests
import fitz  # PyMuPDF
import json

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
