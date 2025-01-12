import json
from openai import OpenAI
import os
key_file_path = os.path.join(os.path.dirname(__file__), 'key.txt')
with open(key_file_path, 'r') as file:
    key = file.read()
client = OpenAI(api_key=key)

def extract_job_data(jd, client):
    result = []
    prompt = """extract detailed information from job description, including only 3 fields: Major, Tech skills and Experience domain. 
                Always output plain JSON without any markdown or formatting. \n
                Job description is:""" + jd
    try:
        # Call the LLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        result = response.choices[0].message.content
        result = json.loads(result)
    except Exception as e:
        result.append({"error": f"Failed to process JD: {e}"})
    return result