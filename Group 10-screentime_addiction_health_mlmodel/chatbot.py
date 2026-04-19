import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def chat_with_ai(question):

    if not question:
        return "Please ask a question."

    # Domain keywords
    allowed_keywords = [
        "screen",
        "phone",
        "digital",
        "addiction",
        "social",
        "internet",
        "sleep",
        "mental",
        "online"
    ]

    # Check if question is related
    if not any(k in question.lower() for k in allowed_keywords):
        return "⚠️ I only answer questions related to digital health, screen time, social media usage, and mental wellbeing."

    prompt = f"""
You are a Digital Health Assistant.

You help users with:
- Screen time addiction
- Social media mental health
- Digital wellbeing
- Sleep problems caused by phone usage
- Reducing phone addiction

Give short helpful advice.

User question:
{question}

Answer:
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()

        return data.get("response", "AI could not generate a response.")

    except Exception as e:
        return f"AI Error: {str(e)}"