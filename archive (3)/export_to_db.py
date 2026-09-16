import re
import spacy
import sqlite3
from pathlib import Path

def clean_text(text): #data cleaning
    """
    Cleans structural noise and URLs while preserving exact 
    character counts for index alignment.
    """
    # urls = re.findall(r'https?://\S+|www\.\S+', text)
    # for url in urls:
    #     text = text.replace(url, " " * len(url)) 
    text = re.sub(r'[\t\r\n]', ' ', text)
    text = re.sub(r'[●•❖➣]', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    
    return text


nlp2 = spacy.load("en_core_web_trf") # Load the English NLP model
text = "OTIENO C. UPENDO Computer Science Student | Data & Systems Engineering Email: ucotieno@gmail.com Mobile: +254 798 380 239 Location: Nairobi, Kenya GitHub: https://github.com/ucotieno LinkedIn: https://linkedin.com/in/ucotieno Portfolio: https://portfolio-4w4q.onrender.com/portfolio.html SUMMARY Third-year Computer Science student (Graduating 2027) at the University of Nairobi with hands-on experience building data pipelines, scraping systems, and backend APIs. Seeking structured industry exposure through internship opportunities to deepen software engineering fundamentals and contribute to reliable, scalable systems. TECHNICAL SKILLS Python, JavaScript Algorithms & Data Structures SQL Data Processing & ETL Workflows Machine Learning Fundamentals Numpy, Pandas Scikit-learn Pytorch, Tensorflow EXPERIENCE Instructor (Contract) | GOMYCODE Kenya 2024 – Present Mentor students in Data Science and Web Development fundamentals. Prepare structured learning materials and practical exercises. Support learners in debugging and implementing projects. Independent Developer (Contract-Based) 2020 – Present Built content extraction pipelines using Python-based tooling. Designed structured scraping workflows for reliable data collection. Developed backend APIs and ETL processes for analytics systems. Delivered contract-based technical solutions with documented outcomes. EDUCATION University of Nairobi BSc. Computer Science (Expected Graduation: 2027) LANGUAGES English: Fluent Swahili: Native"
text = clean_text(text)


doc2 = nlp2(text)
for ent in doc2.ents:
    print(ent.text, ent.label_)
    if ent.label_ == "PERSON":
        path = Path(r"C:\Users\25471\Desktop\Resume Parser Project\resume_parser_db.db")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        query = "INSERT INTO candidates (name) VALUES (?)"
        cursor.execute(query, (ent.text,))
        conn.commit()
        conn.close()

print("Data inserted successfully!")