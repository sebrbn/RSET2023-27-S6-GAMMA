import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_llm_advice(parsed_resume, job_opening, ranking):

    resume_skills = parsed_resume.get("skills", [])
    experience = parsed_resume.get("experience", 0)

    missing = ranking["missing_skills"]

    prompt = f"""
You are an expert AI recruiter.

Analyze the candidate resume and job description.

Job Title: {job_opening.title}

Job Description:
{job_opening.description}

Required Skills:
{job_opening.required_skills}

Candidate Skills:
{resume_skills}

Candidate Experience:
{experience} years

Matched Skills Score:
{ranking['skill_match']}

Missing Skills:
{missing}

Overall Score:
{ranking['score']}

Explain:
1. Why the candidate scored this value
2. What skills are missing
3. How the candidate can improve their resume
4. Suggest specific projects or tools they should add

Keep the answer concise.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful AI career advisor."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
