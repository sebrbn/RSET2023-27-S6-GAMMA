# ---------------------------------------------------
# CANDIDATE FEEDBACK ENGINE
# ---------------------------------------------------

def generate_candidate_feedback(parsed_data, ranking_data, job_opening):

    skills = parsed_data["skills"]
    exp = parsed_data["experience"]

    if isinstance(job_opening, dict):
        required_skills = job_opening.get("required_skills", "")
        required_exp = job_opening.get("experience_required", 0)
    else:
        required_skills = job_opening.required_skills
        required_exp = job_opening.experience_required

    required_skills = [
        s.strip() for s in required_skills.split(",")
    ] if required_skills else []

    missing = [
        s for s in required_skills if s not in skills
    ]

    feedback = {
        "score": ranking_data["score"],
        "missing_skills": missing,
        "experience_gap": max(0, required_exp - exp),
        "suggestions": []
    }

    # Suggestions
    if missing:
        feedback["suggestions"].append(
            "Add projects showcasing: " +
            ", ".join(missing)
        )

    if exp < required_exp:
        feedback["suggestions"].append(
            "Gain more practical experience."
        )

    if not feedback["suggestions"]:
        feedback["suggestions"].append(
            "Excellent profile for this role."
        )

    return feedback
