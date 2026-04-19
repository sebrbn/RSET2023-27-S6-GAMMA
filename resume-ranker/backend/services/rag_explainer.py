# ---------------------------------------------------
# RAG EXPLAINABILITY ENGINE (DICT + OBJECT SAFE)
# ---------------------------------------------------
import json

def generate_rag_explanation(parsed_resume, job_opening, ranking):
    """
    Generates explainable reasoning for resume ranking
    Works with BOTH dict and SQLAlchemy objects
    """

    print("\n========== RAG START ==========")

    # ---------------------------------------------------
    # SAFE FIELD EXTRACTION
    # ---------------------------------------------------

    if isinstance(job_opening, dict):
        required_skills = job_opening.get("required_skills", [])
        experience_required = job_opening.get("experience_required", 0)
        title = job_opening.get("title", "Unknown Role")

    else:
        required_skills = getattr(job_opening, "required_skills", [])
        experience_required = getattr(job_opening, "experience_required", 0)
        title = getattr(job_opening, "title", "Unknown Role")

    # If skills stored as string → convert to list
    # Safely convert skills from DB
    if isinstance(required_skills, str):

        try:
            required_skills = json.loads(required_skills)

            # Handle nested lists
            if isinstance(required_skills, list) and len(required_skills) == 1 and isinstance(required_skills[0], list):
                required_skills = required_skills[0]

        except:
            required_skills = [
                s.strip().lower()
                for s in required_skills.split(",")
                if s.strip()
            ]

    # Clean skills
    required_skills = [
        str(s)
        .replace('"','')
        .replace('[','')
        .replace(']','')
        .strip()
        .lower()
        for s in required_skills
    ]
   

    # ---------------------------------------------------
    # RESUME DATA
    # ---------------------------------------------------

    resume_skills = [s.lower().strip() for s in parsed_resume.get("skills", [])]
    experience = parsed_resume.get("experience", 0)

    matched_skills = [
        s for s in required_skills
        if s in resume_skills
    ]

    missing_skills = [
        s for s in required_skills
        if s not in resume_skills
    ]

    # ---------------------------------------------------
    # BUILD EXPLANATION TEXT
    # ---------------------------------------------------

    explanation = f"""
JOB ROLE: {title}

MATCHED SKILLS:
{', '.join(matched_skills) if matched_skills else 'None'}

MISSING SKILLS:
{', '.join(missing_skills) if missing_skills else 'None'}

CANDIDATE EXPERIENCE:
{experience} years

REQUIRED EXPERIENCE:
{experience_required} years

FINAL SCORE:
{ranking.get('score', 0)} %
"""

    print("RAG Generated Successfully")
    print("========== RAG END ==========\n")

    return explanation.strip()