import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from extract_text import extract
from pathlib import Path

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the prompt ONCE
with open("prompt.txt", "r") as file:
    base_prompt = file.read()

predicted_outputs = []

path = Path(r"C:\Users\25471\Desktop\Resume Parser Project\resume_samples")
output_dir = Path(r"C:\Users\25471\Desktop\Resume Parser Project\parsed_resumes")

# Make sure output folder exists
output_dir.mkdir(parents=True, exist_ok=True)

# Process each resume
for file in path.iterdir():

    # Only process PDF and DOCX files
    if not file.is_file() or file.suffix.lower() not in {".pdf", ".docx", ".png", ".jpg", ".jpeg"}:
        continue

    print(f"Processing: {file.name}")

    try:
        # Extract resume text
        result = extract(str(file))
        resume_dict = result.to_dict()
        resume_text = resume_dict["text"]

        # Create a fresh prompt for THIS resume
        full_prompt = base_prompt + f"\n{resume_text}"

        # Send request to OpenAI
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=full_prompt,
        )

        predictions = response.output_text

        # Convert model response from JSON string to Python object
        parsed_resume = json.loads(predictions)

        # Add source filename
        if isinstance(parsed_resume, dict):
            parsed_resume["source_file"] = file.name

        elif isinstance(parsed_resume, list):
            for resume in parsed_resume:
                if isinstance(resume, dict):
                    resume["source_file"] = file.name

        # Store the parsed JSON object
        predicted_outputs.append(parsed_resume)

        print(f"Successfully processed: {file.name}")

    except Exception as e:

        print(f"Error processing {file.name}: {e}")

        # Store error instead of stopping entire batch
        predicted_outputs.append({
            "source_file": file.name,
            "error": str(e)
        })


# Save all results
output_file = output_dir / "parsed_resumes.json"

with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(
        predicted_outputs,
        json_file,
        indent=4,
        ensure_ascii=False
    )

print(f"\nSuccessfully processed batch.")
print(f"Output saved to: {output_file}")