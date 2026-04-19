import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_recommendation(score, level, health):
    """
    Get personalized AI recommendation in bullet points with short explanations.
    """
    prompt = f"""
You are a digital health expert. A user has the following results:

- Addiction Score: {score}
- Addiction Level: {level}
- Health Classification: {health}

Provide 5 actionable recommendations to improve digital wellbeing, mental health,
sleep quality, and productivity. 

Each recommendation should have a **title** (few words) and a short explanation (1-2 sentences). 
Format the output like this:

Title: Explanation
Title: Explanation
...
    """

    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        result = response.json()
        text = result.get("response", "")

        # Split into points
        points = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                # Remove numbering/bullets if present
                line = line.lstrip("0123456789.-* )").strip()
                points.append(line)

        return points

    except Exception as e:
        print(f"Error in AI recommendation: {e}")
        return ["AI recommendation service unavailable"]