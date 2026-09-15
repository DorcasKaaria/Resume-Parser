import os
from openai import OpenAI
from extract_text import extract

os.environ["OPENAI_API_KEY"] = ""

client = OpenAI()

with open("prompt.txt", "r") as fo:
	prompt = fo.read()


result = extract("/home/voyager/Downloads/Dorcas_Kaaria_Resume_HR_Business_Reporting_Analyst.pdf")
resume_dict = result.to_dict()
resume_text = resume_dict["text"]

prompt += f"\n{resume_text}"

response = client.responses.create(
    model="gpt-5.6-luna",
    input=prompt,
)

print(response.output_text)
