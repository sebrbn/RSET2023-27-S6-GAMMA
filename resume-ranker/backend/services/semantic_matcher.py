from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')


def semantic_skill_match(resume_skills, job_skills):

    matched = []

    for r in resume_skills:

        r_vec = model.encode([r])

        for j in job_skills:

            j_vec = model.encode([j])

            sim = cosine_similarity(r_vec, j_vec)[0][0]

            if sim > 0.65: # similarity threshold
                matched.append(j)

    return list(set(matched))