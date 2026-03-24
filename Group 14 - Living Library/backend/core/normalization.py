import re


def normalize_relation(rel: str) -> str:
    """Legacy function — simple uppercase + underscore."""
    return rel.strip().upper().replace(" ", "_")


def safe_rel(rel: str) -> str:
    """
    Sanitize a relation string for safe Neo4j/graph usage.
    - Uppercase
    - Replace non-alphanumeric with underscore
    - Collapse multiple underscores
    - Ensure starts with a letter
    """
    rel = re.sub(r"[^A-Za-z0-9_]", "_", (rel or "").upper())
    rel = re.sub(r"_+", "_", rel).strip("_")
    if not rel or not rel[0].isalpha():
        rel = "REL_" + (rel or "UNKNOWN")
    return rel
