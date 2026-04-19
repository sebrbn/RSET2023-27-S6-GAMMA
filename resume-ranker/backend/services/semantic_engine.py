# ---------------------------------------------------
# SEMANTIC NORMALIZATION ENGINE
# ---------------------------------------------------

from services.skill_ontology import SKILL_ONTOLOGY


# ---------------------------------------------------
# BUILD SYNONYM MAP
# ---------------------------------------------------
def build_synonym_map():

    synonym_map = {}

    for canonical, variants in SKILL_ONTOLOGY.items():

        for variant in variants:
            synonym_map[variant.lower()] = canonical

    return synonym_map


SYNONYM_MAP = build_synonym_map()


# ---------------------------------------------------
# NORMALIZE SKILLS
# ---------------------------------------------------
def normalize_skills(extracted_skills):

    normalized = []

    for skill in extracted_skills:

        key = skill.lower()

        if key in SYNONYM_MAP:
            normalized.append(SYNONYM_MAP[key])
        else:
            normalized.append(skill)

    return list(set(normalized))
