import os
import json
import PyPDF2
import argparse
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel

try:
    key_file_path = os.path.join(os.path.dirname(__file__), 'ali_key.txt')
    with open(key_file_path, 'r') as file:
        key = file.read()
    client = OpenAI(
        api_key=key, 
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    ) # "https://api.deepseek.com"
    model_name = "qwen-plus" # "deepseek-chat"
    test_response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": "Hi"},
        ],
    )
    print('Using QWEN from Ali.')
except:
    try:
        key_file_path = os.path.join(os.path.dirname(__file__), 'key.txt')
        with open(key_file_path, 'r') as file:
            key = file.read()
        client = OpenAI(
            api_key=key,
        )
        model_name = "gpt-4o-mini"
        test_response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hi"},
            ],
        )
        print('Using GPT from OpenAI.')
    except:
        print('No valid API key found. Please provide a valid API key in a text file named "key.txt" or "ali_key.txt" in the same directory as the script.')

class ExperienceType(Enum):
    DETAIL = 1
    SUMMARY = 2
    SENTENCE = 3

class DatailedExperience(BaseModel):
    job_title: str
    organization: str
    start_date: str
    end_date: str
    description: str

class SummaryExperience(BaseModel):
    job_title: str
    organization: str
    business_task: str
    result: str
    skill_stack: str
    duration: str

class DetailResume(BaseModel):
    name: str
    school: list[str]
    gpa: list[str]
    major: list[str]
    graduation_time: str
    tech_skills: list[str]
    business_domain: list[str]
    experiences: list[DatailedExperience]

class SummaryResume(BaseModel):
    name: str
    school: list[str]
    gpa: list[str]
    major: list[str]
    graduation_time: str
    tech_skills: list[str]
    business_domain: list[str]
    experiences: list[SummaryExperience]

class BriefResume(BaseModel):
    name: str
    school: list[str]
    gpa: list[str]
    major: list[str]
    graduation_time: str
    tech_skills: list[str]
    business_domain: list[str]
    experiences: list[str]

def read_resume(file_path=None, file_object=None, detailed_level=ExperienceType.SENTENCE):
    print(model_name)
    error_message = ''

    # Handle file path input
    if file_path:
        if os.path.exists(file_path) and file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                return extract_student_info(file, detailed_level)
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
            raise Exception(error_message)

        if file_object.name.endswith('.pdf'):
            return extract_student_info(file_object, detailed_level)

        error_message += " and invalid file object format. Please upload a PDF file."
        raise Exception(error_message)

    # If no valid inputs provided
    error_message += "No file path or file object provided."
    raise Exception(error_message)

def extract_student_info(file, detailed_level=ExperienceType.SENTENCE):
    text = extract_text_from_pdf(file)
    llm_response = llm_parse(text, detailed_level)
    return json.loads(llm_response)

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def llm_parse(text, detailed_experience=False):
    if detailed_experience == ExperienceType.DETAIL:
        experiment_prompt = "detailed experiences (include work, intern, project, and others) with job title, organization, start and end date (YYYY-MM or present), and description from the student resume."
        resume_schema = DetailResume.model_json_schema()
    elif detailed_experience == ExperienceType.SUMMARY:
        experiment_prompt = "summarized experiences (include work, intern, project, and others) with job title, organization, business_task (for about 20 words), result, skill_stack, and duration in month (e.g. 3 months) from the student resume."
        resume_schema = SummaryResume.model_json_schema()
    else:
        experiment_prompt = "summarized experiences, each in one or two sentences."
        resume_schema = BriefResume.model_json_schema()
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {'role': 'system', 'content': """You are a recruiter looking to extract information from a student resume. 
Extract the name, school(s), gpa(s) (e.g. 3.85/4.00), major(s) (without degree, e.g. Master of Science in Information should be Information Science), graduation_time (YYYY-MM), tech_skills (e.g., Python, SQL), business_domain(s) (or industry of company despite schools, at least two, e.g., finance, supply chain) and """ + experiment_prompt + """ 
Always output plain JSON without any markdown or formatting, only the raw JSON object. Please respond in English.
JSON SCHEMA: {"name": str, "school": list[str], "gpa": list[str], major: list[str], graduation_time: str, tech_skills: list[str], business_domain: list[str], experiences: list[str]}"""},
            {"role": "user", "content": """Resume
    """ + text},
        ],
        response_format={'type': 'json_schema', 'json_schema': {'name': 'resume', 'schema': resume_schema}},
        temperature=0.00,
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resume Reader')
    parser.add_argument('--file_path', type=str, help='Path to the resume PDF file')
    parser.add_argument('--detailed_level', type=str, default='SENTENCE', 
                        help='Level of detail to extract from the resume',
                        choices=['DETAIL', 'SUMMARY', 'SENTENCE'], required=False)
    parser.add_argument('--output', type=str, help='Output file path', required=False)
    args = parser.parse_args()
    result = read_resume(args.file_path, detailed_level=ExperienceType[args.detailed_level])
    if 'error' in result:
        print(result['error'])
    elif args.output:
        with open(args.output, 'w') as file:
            json.dump(result, file)
        print("Resume data extracted successfully and saved to", args.output)
    else:
        print(json.dumps(result, indent=4))

