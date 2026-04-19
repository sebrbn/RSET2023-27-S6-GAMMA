# ---------------------------------------------------
# EMBEDDING-BASED SEMANTIC MATCHER
# ---------------------------------------------------

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from services.skill_ontology import SKILL_ONTOLOGY


# Load model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ---------------------------------------------------
# BUILD SKILL EMBEDDINGS
# ---------------------------------------------------
def build_skill_embeddings():

    skill_sentences = []
    skill_labels = []

    for canonical, variants in SKILL_ONTOLOGY.items():

        for phrase in variants:
            skill_sentences.append(phrase)
            skill_labels.append(canonical)

    embeddings = model.encode(skill_sentences)

    return embeddings, skill_labels


SKILL_EMBEDDINGS, SKILL_LABELS = build_skill_embeddings()


# ---------------------------------------------------
# SEMANTIC SKILL DETECTION
# ---------------------------------------------------
def detect_semantic_skills(sentences, threshold=0.6):

    detected_skills = set()

    for sentence in sentences:

        sentence_embedding = model.encode([sentence])

        similarities = cosine_similarity(
            sentence_embedding,
            SKILL_EMBEDDINGS
        )[0]

        for i, score in enumerate(similarities):

            if score >= threshold:
                detected_skills.add(SKILL_LABELS[i])

    return list(detected_skills)
