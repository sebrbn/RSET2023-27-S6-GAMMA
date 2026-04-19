# ---------------------------------------------------
# AI HIRING SUMMARY GENERATOR
# ---------------------------------------------------

def generate_ai_summary(parsed_data, ranking_data, job_opening):

    resume_skills = parsed_data["skills"]
    experience = parsed_data["experience"]

    # Handle dict or DB object
    if isinstance(job_opening, dict):
        required_skills = job_opening.get("required_skills", "")
        required_exp = job_opening.get("experience_required", 0)
        title = job_opening.get("title", "Candidate")
    else:
        required_skills = job_opening.required_skills
        required_exp = job_opening.experience_required
        title = job_opening.title

    required_skills = [
        s.strip() for s in required_skills.split(",")
    ] if required_skills else []

    missing = ranking_data["missing_skills"]

    # ---------------------------------------------------
    # BUILD SUMMARY
    # ---------------------------------------------------
    strengths = []
    weaknesses = []

    for skill in resume_skills:
        if skill in required_skills:
            strengths.append(skill)

    for skill in required_skills:
        if skill not in resume_skills:
            weaknesses.append(skill)

    summary = f"""
AI Hiring Insight — {title}

Strengths:
{", ".join(strengths) if strengths else "General skill alignment"}

Weaknesses:
{", ".join(weaknesses) if weaknesses else "No major gaps"}

Experience:
Candidate: {experience} years
Required: {required_exp} years

Recommendation:
"""

    if ranking_data["score"] >= 85:
        summary += "Highly suitable for the role."
    elif ranking_data["score"] >= 60:
        summary += "Moderately suitable — can be considered."
    else:
        summary += "Not recommended currently."

    return summary
