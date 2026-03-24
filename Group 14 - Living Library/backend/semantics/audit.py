# audit.py
# Enhanced Audit Lab Logic (60% Upgrade)
# Includes:
# - Semantic claim verification
# - Confidence scoring
# - Truth score computation
# - Semantic drift detection
# - Explainability mapping

from sentence_transformers import SentenceTransformer, util
import torch


# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


# ------------------------------------------------------------
# Utility: Compute semantic similarity
# ------------------------------------------------------------
def compute_similarity(text1, text2):
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2)
    return float(similarity)


# ------------------------------------------------------------
# Semantic Drift Detection
# ------------------------------------------------------------
def semantic_drift_score(answer, supporting_facts):
    """
    Compute drift against top-k supporting facts only.
    """
    if not supporting_facts:
        return {"similarity": 0, "drift_score": 1, "drift_level": "High"}

    similarities = []

    for fact in supporting_facts:
        sim = compute_similarity(answer, fact)
        similarities.append(sim)

    avg_similarity = sum(similarities) / len(similarities)
    drift = 1 - avg_similarity

    if drift < 0.1:
        level = "Low"
    elif drift < 0.3:
        level = "Moderate"
    else:
        level = "High"

    return {
        "similarity": round(avg_similarity, 3),
        "drift_score": round(drift, 3),
        "drift_level": level
    }
# ------------------------------------------------------------
# Audit Claim
# ------------------------------------------------------------
def cluster_similar_claims(claims, similarity_threshold=0.9):
    """
    Removes semantically duplicate claims using similarity.
    """
    unique_claims = []

    for claim in claims:
        is_duplicate = False
        for existing in unique_claims:
            if compute_similarity(claim, existing) >= similarity_threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_claims.append(claim)

    return unique_claims

# ------------------------------------------------------------
# Enhanced Claim Verification
# ------------------------------------------------------------
def audit_claim(claim, stored_facts, threshold=0.75):
    """
    Verifies claim using semantic similarity.
    Returns structured result.
    """

    best_match = None
    best_score = 0

    for fact in stored_facts:
        score = compute_similarity(claim, fact)
        if score > best_score:
            best_score = score
            best_match = fact

    if best_score >= threshold:
        status = "Verified"
    else:
        status = "External"

    return {
        "claim": claim,
        "status": status,
        "confidence": round(best_score, 3),
        "supporting_fact": best_match if status == "Verified" else None
    }


# ------------------------------------------------------------
# Audit Multiple Claims
# ------------------------------------------------------------
def audit_all_claims(claims, stored_facts):
    results = []
    for claim in claims:
        result = audit_claim(claim, stored_facts)
        results.append(result)
    return results

# ------------------------------------------------------------
# Detect contradictions
# ------------------------------------------------------------
def detect_contradictions(triples):
    """
    Detect conflicting triples:
    Same subject + relation but different object.
    """
    contradictions = []
    seen = {}

    for s, r, o in triples:
        key = (s.lower(), r.lower())

        if key in seen:
            if seen[key] != o.lower():
                contradictions.append({
                    "subject": s,
                    "relation": r,
                    "values": [seen[key], o]
                })
        else:
            seen[key] = o.lower()

    return contradictions

# ------------------------------------------------------------
# Compute Weighted Truth Score
# ------------------------------------------------------------
def compute_truth_score(audit_results, contradictions):
    if not audit_results:
        return {
            "truth_score": 0,
            "total_claims": 0,
            "verified": 0,
            "external": 0
        }

    total = len(audit_results)
    verified = sum(1 for r in audit_results if r["status"] == "Verified")
    external = total - verified

    avg_confidence = (
        sum(r["confidence"] for r in audit_results if r["status"] == "Verified") 
        / verified
        if verified > 0 else 0
    )

    contradiction_penalty = len(contradictions) * 0.1

    truth_score = (0.7 * avg_confidence) - contradiction_penalty

    truth_score = max(0, truth_score) * 100

    return {
        "truth_score": round(truth_score, 2),
        "total_claims": total,
        "verified": verified,
        "external": external,
        "contradictions": len(contradictions)
    }

# ------------------------------------------------------------
# Recommend Action
# ------------------------------------------------------------
def recommend_action(truth_data, drift_data):
    """
    Suggest next system action based on audit results.
    This prepares the system for a future ReAct-style reasoning loop.
    """

    truth_score = truth_data["truth_score"]
    contradictions = truth_data["contradictions"]
    drift_level = drift_data["drift_level"]

    if contradictions > 0:
        return "verify_conflicting_facts"

    if truth_score < 50:
        return "expand_graph_search"

    if drift_level == "High":
        return "retrieve_additional_context"

    return "answer_verified"

# ------------------------------------------------------------
# Explainability Mapping
# ------------------------------------------------------------
def explain_answer(answer, stored_facts, top_k=3):
    """
    Rank supporting facts by similarity.
    Removes duplicate statements.
    """
    raw_sentences = [s.strip() for s in answer.split(".") if s.strip()]
    
    # Remove duplicate sentences
    sentences = []
    for s in raw_sentences:
        if s not in sentences:
            sentences.append(s)

    explanations = []

    for sentence in sentences:
        scored = []

        for fact in stored_facts:
            score = compute_similarity(sentence, fact)
            scored.append((fact, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_support = scored[:top_k]

        explanations.append({
            "statement": sentence,
            "supporting_facts": [
                {"fact": f, "score": round(s, 3)} 
                for f, s in top_support
            ]
        })

    return explanations

# ------------------------------------------------------------
# Master Audit Report (UI Ready)
# ------------------------------------------------------------
def audit_report(original_text, generated_answer, stored_facts, triples=None):
    """
    Full 75% upgraded audit pipeline.
    """

    # Step 1: Extract claims
    claims = [c.strip() for c in generated_answer.split(".") if c.strip()]

    # Step 2: Remove duplicates
    claims = cluster_similar_claims(claims)

    # Step 3: Verify claims
    audit_results = audit_all_claims(claims, stored_facts)

    # Step 4: Detect contradictions (if triples available)
    contradictions = detect_contradictions(triples) if triples else []

    # Step 5: Compute truth score
    truth_data = compute_truth_score(audit_results, contradictions)

    # Step 6: Compute drift (using stored facts)
    drift_data = semantic_drift_score(generated_answer, stored_facts)

    action = recommend_action(truth_data, drift_data)

    # Step 7: Explainability
    explanations = explain_answer(generated_answer, stored_facts)

    return {
    "truth_analysis": truth_data,
    "drift_analysis": drift_data,
    "contradictions": contradictions,
    "claims_analysis": audit_results,
    "explainability": explanations,
    "action_recommendation": action
}

# ------------------------------------------------------------
# Standalone Test
# ------------------------------------------------------------
if __name__ == "__main__":

    # sample data for testing
    stored_facts = [
        "Water boils at 100C",
        "Water boils at 50C",
        "Plants use chlorophyll",
        "Photosynthesis produces oxygen"
    ]

    triples = [
        ("Water", "boils_at", "100C"),
        ("Water", "boils_at", "50C"),
        ("Plants", "use", "chlorophyll")
    ]

    original_text = "Water boils at 100C under normal conditions."

    generated_answer = (
        "Water boils at 100C. "
        "Water boils at 50C. "
        "Plants use chlorophyll."
    )

    report = audit_report(original_text, generated_answer, stored_facts, triples)

    print("\n===== 75% AUDIT TEST OUTPUT =====\n")

    print("TRUTH ANALYSIS")
    print("-----------------")
    for key, value in report["truth_analysis"].items():
        print(f"{key}: {value}")

    print("\nDRIFT ANALYSIS")
    print("-----------------")
    for key, value in report["drift_analysis"].items():
        print(f"{key}: {value}")

    print("\nSYSTEM ACTION")
    print("-----------------")
    print(report["action_recommendation"])