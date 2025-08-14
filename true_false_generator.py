import requests
from config import TOGETHER_API_KEY, TOGETHER_URL, MODEL_NAME

def generate_true_false(text, num_questions=5):
    prompt = f"""Generate {num_questions} True/False questions from the following text.

Each question should be on a single line followed by "Answer: True" or "Answer: False".

Example format:
1. The Earth revolves around the Sun. Answer: True
2. Water boils at 50 degrees Celsius. Answer: False

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
