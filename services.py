# services.py

import requests
import pdfplumber
from config import TOGETHER_API_KEY, TOGETHER_URL, MODEL_NAME

def extract_text_from_pdf(file, num_pages):
    text = ""
    with pdfplumber.open(file) as pdf:
        for i in range(min(num_pages, len(pdf.pages))):
            page = pdf.pages[i]
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def generate_mcq(text, num_questions=5):
    prompt = f"""
Generate {num_questions} multiple choice questions from the following text.

Each question should be on a single line, and each answer option should be on its own line (a-d), like this:

Example format:
1. What is the capital of France?
a) Berlin
b) Madrid
c) Paris
d) Rome
Answer: c) Paris

Now use this format to generate questions from the following text:
{text}
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 0.9
    }

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(TOGETHER_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"❌ API Error: {response.status_code} - {response.text}"
