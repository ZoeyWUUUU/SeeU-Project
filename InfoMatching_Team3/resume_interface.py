import os
import json
import PyPDF2
from openai import OpenAI
from pydantic import BaseModel

key_file_path = os.path.join(os.path.dirname(__file__), 'keys.txt')
with open(key_file_path, 'r') as file:
    key = file.read()

client = OpenAI(api_key=key)


class Experience(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: str
    description: str

class Resume(BaseModel):
    name: str
    school: list[str]
    gpa: list[str]
    major: list[str]
    graduation_time: str
    tech_skills: list[str]
    business_domain: list[str]
    experiences: list[Experience]


def read_resume(file_path=None, file_object=None):
    error_message = ''

    # Handle file path input
    if file_path:
        if os.path.exists(file_path) and file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                return extract_student_info(file)
        if not os.path.exists(file_path):
            error_message = "File does not exist at " + file_path + ","
        elif not file_path.endswith('.pdf'):
            error_message = "File path does not end with .pdf," 
        else:
            error_message = "Invalid file path," 

    # Handle file object input
    if file_object:
        if not hasattr(file_object, 'read') or not hasattr(file_object, 'name'):
            error_message += " and no valid file object provided."
            return {"error": error_message}

        if file_object.name.endswith('.pdf'):
            return extract_student_info(file_object)

        error_message += " and invalid file object format. Please upload a PDF file."
        return {"error": error_message}

    # If no valid inputs provided
    error_message += "No file path or file object provided."
    return {"error": error_message}


def extract_student_info(file):
    text = extract_text_from_pdf(file)
    llm_response = llm_parse(text)
    return json.loads(llm_response)


def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text


def llm_parse(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 'content': """You are a recruiter looking to extract information from a student resume. 
Extract the name, school, gpa (e.g. 3.85/4.00), major (without degree, e.g. Master of Science in Information should be Information Science), graduation_time (YYYY-MM), tech_skills (e.g., Python, SQL), business_domain (or industry, at least one, e.g., finance, supply chain) and detailed experiences (include work, intern, project, and others) with title, company, start and end date (YYYY-MM or present), and description from the student resume. 
Always output plain JSON without any markdown or formatting, only the raw JSON object. """},
            {"role": "user", "content": """Resume
    """ + text},
        ],
        response_format={'type': 'json_schema', 'json_schema': {'name': 'resume', 'schema': Resume.model_json_schema()}},
    )
    return response.choices[0].message.content

