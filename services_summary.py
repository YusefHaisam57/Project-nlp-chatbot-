# services_summary.py

import requests
from config import TOGETHER_API_KEY, TOGETHER_URL, MODEL_NAME

def summarize_text(text, num_sentences=5):
    prompt = f"""
Summarize the following text in about {num_sentences} concise sentences. Focus on the key ideas and avoid unnecessary details.

Text:
{text}
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
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
