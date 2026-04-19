# ---------------------------------------------------
# JOB DESCRIPTION PARSER
# ---------------------------------------------------

import re


# ---------------------------------------------------
# EXTRACT SKILLS FROM JD
# ---------------------------------------------------
def extract_jd_skills(description, skill_db):

    description = description.lower()

    matched_skills = []

    for skill in skill_db:
        if skill.lower() in description:
            matched_skills.append(skill)

    return list(set(matched_skills))


# ---------------------------------------------------
# EXTRACT EXPERIENCE FROM JD
# ---------------------------------------------------
def extract_jd_experience(description):

    pattern = r'(\d+)\s*(years|year)'

    match = re.search(pattern, description.lower())

    if match:
        return int(match.group(1))

    return 0
