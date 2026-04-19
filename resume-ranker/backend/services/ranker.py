# ---------------------------------------------------
# RANKER — SEMANTIC + NORMALIZED VERSION
# ---------------------------------------------------

import json

from services.jd_parser import (
    extract_jd_skills,
    extract_jd_experience
)

from services.skill_ontology import SKILL_ONTOLOGY
from services.semantic_matcher import semantic_skill_match


# ---------------------------------------------------
# 🔥 BUILD MASTER SKILL DATABASE
# ---------------------------------------------------
def build_skill_database():

    skill_db = []

    for role in SKILL_ONTOLOGY.values():
        for category in role.values():
            skill_db.extend(category)

    return list(set(skill_db))


# ---------------------------------------------------
# 🔥 NORMALIZE SKILLS USING ONTOLOGY
# ---------------------------------------------------
def normalize_skill(skill: str):

    skill = skill.lower().strip()

    for role in SKILL_ONTOLOGY.values():
        for category in role.values():
            for canonical in category:

                # Exact match
                if skill == canonical.lower():
                    return canonical.lower()

                # Synonym match
                if skill == canonical.lower():
                    return canonical.lower()

    return skill


# ---------------------------------------------------
# 🔥 SKILL MATCH SCORE
# ---------------------------------------------------
def skill_match_score(resume_skills, jd_skills):

    if not jd_skills:
        return 0

    matched = semantic_skill_match(resume_skills, jd_skills)

    return (len(matched) / len(jd_skills)) * 100


# ---------------------------------------------------
# 🔥 EXPERIENCE SCORE
# ---------------------------------------------------
def experience_score(resume_exp, jd_exp):

    if jd_exp == 0:
        return 100

    if resume_exp >= jd_exp:
        return 100

    return (resume_exp / jd_exp) * 100


# ---------------------------------------------------
# 🚀 FINAL RANK FUNCTION
# ---------------------------------------------------
def rank_resume(parsed_resume, job_opening):

    print("\n========== RANKING START ==========")

    # ---------------------------------------------------
    # 1️⃣ EXTRACT RESUME DATA
    # ---------------------------------------------------
    resume_skills_raw = parsed_resume.get(
        "skills", []
    )

    experience_years = float(parsed_resume.get(
        "experience", 0
    ))

    # Normalize resume skills
    resume_skills = [
        normalize_skill(skill)
        for skill in resume_skills_raw
    ]


    # ---------------------------------------------------
    # 2️⃣ HANDLE SQLAlchemy OR Dict
    # ---------------------------------------------------
    if isinstance(job_opening, dict):

        required_skills_raw = job_opening.get(
            "required_skills", ""
        )

        required_experience = job_opening.get(
            "experience_required", 0
        )

    else:

        required_skills_raw = (
            job_opening.required_skills
        )

        required_experience = (
            job_opening.experience_required
        )


    # ---------------------------------------------------
    # 3️⃣ 🔥 PARSE DB SKILLS SAFELY
    # ---------------------------------------------------
    required_skills = []

    if isinstance(required_skills_raw, str):

        try:
            # Case 1 — JSON string
            required_skills = []

            if isinstance(required_skills_raw, str):

                try:
                    required_skills = json.loads(required_skills_raw)

                    # Fix nested list
                    if isinstance(required_skills, list) and len(required_skills) == 1 and isinstance(required_skills[0], list):
                        required_skills = required_skills[0]

                except:
                    required_skills = [
                        s.strip().lower()
                        for s in required_skills_raw.split(",")
                        if s.strip()
                    ]

            elif isinstance(required_skills_raw, list):

                # Flatten nested lists
                for s in required_skills_raw:
                    if isinstance(s, list):
                        required_skills.extend(s)
                    else:
                        required_skills.append(s)

            required_skills = [
                str(s)
                .replace('"', '')
                .replace('[', '')
                .replace(']', '')
                .strip()
                .lower()
                for s in required_skills
                if str(s).strip()
            ]

            if len(required_skills) == 1 and isinstance(required_skills[0], list):
                required_skills = required_skills[0]

        except:
            # Case 2 — comma string
            required_skills = [
                s.strip().lower()
                for s in required_skills_raw.split(",")
                if s.strip()
            ]

    elif isinstance(required_skills_raw, list):

        # Case 3 — already list
        required_skills = [
            str(s).strip()
            for s in required_skills_raw
        ]

    else:
        required_skills = []


    # ---------------------------------------------------
    # 4️⃣ NORMALIZE JD SKILLS
    # ---------------------------------------------------
    required_skills = [
        normalize_skill(skill)
        for skill in required_skills
        if skill.strip()
    ]


    # ---------------------------------------------------
    # DEBUG PRINTS
    # ---------------------------------------------------
    print("\n========== SKILL MATCH DEBUG ==========")
    print("RESUME SKILLS:", resume_skills)
    print("JOB SKILLS:", required_skills)
    print("=======================================\n")


    # ---------------------------------------------------
    # 5️⃣ SKILL MATCHING
    # ---------------------------------------------------
    matched = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing = list(
        set(required_skills) - set(matched)
    )

    skill_match = (
        len(matched) / len(required_skills) * 100
        if required_skills else 0
    )


    # ---------------------------------------------------
    # 6️⃣ EXPERIENCE MATCH
    # ---------------------------------------------------
    if required_experience:

        experience_match = min(
            (experience_years /
             required_experience) * 100,
            100
        )

    else:
        experience_match = 0


    # ---------------------------------------------------
    # 7️⃣ FINAL SCORE
    # ---------------------------------------------------
    final_score = (
        (skill_match * 0.7) +
        (experience_match * 0.3)
    )

    print("Matched Skills:", matched)
    print("Missing Skills:", missing)
    print("Score:", final_score)

    print("========== RANKING END ==========\n")


    return {

        "score": round(final_score, 2),
        "skill_match": round(skill_match, 2),
        "experience_match": round(
            experience_match, 2
        ),
        "missing_skills": ", ".join(missing)
    }
