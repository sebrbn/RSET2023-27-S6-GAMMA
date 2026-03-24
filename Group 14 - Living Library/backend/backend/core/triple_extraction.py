# ============================================================
# Enhanced S-R-O Triple Extraction (spaCy 3.8+)
#
# IMPROVEMENTS OVER ORIGINAL:
# 1) Use sentence ROOT predicate (plus conj verbs) instead of all VERBs
# 2) Controlled entity span (no full subtree leaks)
# 3) Copular handling (X is Y) => (X, IS_A/IS, Y)
# 4) Passive handling (X is characterized by Y) => (X, CHARACTERIZE, Y)
# 5) Conjunction objects => multiple triples
# 6) "from ... to ..." => RANGE_FROM / RANGE_TO
# 7) Negation/modality prefixes (NOT_, MAY_/CAN_/MUST_...)
# 8) Simple pronoun resolution with memory
# 9) Better entity extraction with noun chunks
# 10) Ordered deduplication
# ============================================================

import re
from typing import List, Tuple, Optional

import spacy

Triple = Tuple[str, str, str]

# Load NLP model once
nlp = spacy.load("en_core_web_sm")

# ============================================================
# CONSTANTS
# ============================================================
PRONOUNS = {"it", "this", "that", "they", "them", "he", "she",
            "his", "her", "their", "its", "these", "those"}
REL_PRONOUNS = {"that", "which", "who", "whom", "whose"}

SUBJ_DEPS = {"nsubj", "nsubjpass", "csubj"}
OBJ_DEPS = {"obj", "dobj", "iobj", "attr", "oprd", "dative", "pobj"}
COP_DEPS = {"cop"}  # is/are/was/were

DROP_SUBTREE_DEPS = {"relcl", "advcl", "acl", "ccomp", "xcomp", "parataxis"}


# ============================================================
# TEXT HELPERS
# ============================================================
def safe_rel(rel: str) -> str:
    """Sanitize a relation string for safe graph usage."""
    rel = re.sub(r"[^A-Za-z0-9_]", "_", (rel or "").upper())
    rel = re.sub(r"_+", "_", rel).strip("_")
    if not rel or not rel[0].isalpha():
        rel = "REL_" + (rel or "UNKNOWN")
    return rel


def clean_text(s: str, max_len: int = 220) -> str:
    """Clean whitespace and strip edge punctuation."""
    s = re.sub(r"\s+", " ", (s or "")).strip()
    s = re.sub(r"^[,;:\-–—\(\)\[\]\{\}]+|[,;:\-–—\(\)\[\]\{\}]+$", "", s).strip()
    return s[:max_len]


def clean_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def is_good_entity(text: str) -> bool:
    """Check if a text string is a valid entity (not a pronoun, not too short)."""
    if not text:
        return False
    t = text.lower().strip()

    if t in PRONOUNS or t in REL_PRONOUNS:
        return False
    if len(t) <= 1:
        return False
    if not re.search(r"[A-Za-z0-9]", t):
        return False

    return True


def pick_salient_entity(doc_or_span) -> Optional[str]:
    """Pick the most salient entity from a doc/span for pronoun resolution."""
    if doc_or_span.ents:
        return max([e.text for e in doc_or_span.ents], key=len)

    try:
        noun_chunks = list(doc_or_span.noun_chunks)
    except Exception:
        noun_chunks = list(doc_or_span.doc.noun_chunks)

    for nc in noun_chunks:
        if is_good_entity(nc.text):
            return nc.text

    return None


# ============================================================
# ENTITY SPAN EXTRACTION (controlled, no clause leaks)
# ============================================================
def token_span_clean(head) -> str:
    """
    Build a compact phrase around a head token:
    - include tight modifiers (compound/amod/poss/nummod/det)
    - optionally include short appositions
    - avoid long clause expansions (relcl/advcl/ccomp/xcomp...)
    """
    if head is None:
        return ""

    span_tokens = {head}

    for ch in head.children:
        if ch.dep_ in DROP_SUBTREE_DEPS:
            continue
        if ch.dep_ in {"compound", "amod", "poss", "nummod", "det"}:
            span_tokens.update(list(ch.subtree))

    # short appos
    for ch in head.children:
        if ch.dep_ == "appos":
            app = " ".join([t.text for t in ch.subtree])
            if len(app.split()) <= 5:
                span_tokens.update(list(ch.subtree))

    toks = sorted(span_tokens, key=lambda t: t.i)
    return clean_text(" ".join([t.text for t in toks]))


def noun_phrase_from_token(tok) -> str:
    """
    Prefer noun_chunk containing tok (cleaned), else controlled head span.
    """
    doc = tok.doc
    try:
        ncs = list(doc.noun_chunks)
    except Exception:
        ncs = []

    for nc in ncs:
        if tok.i >= nc.start and tok.i < nc.end:
            txt = nc.text
            # cut at relative pronouns to avoid "X which ..."
            txt = re.split(r"\b(which|that|who|whom|whose)\b", txt, maxsplit=1)[0].strip()
            return clean_text(txt)

    return token_span_clean(tok)


# ============================================================
# PREDICATE SELECTION (Span.root)
# ============================================================
def main_predicates(sent_span) -> List:
    """
    Use sentence root if it's VERB/AUX.
    Include its verb conj siblings.
    """
    root = sent_span.root
    preds = []

    if root.pos_ in {"VERB", "AUX"}:
        preds.append(root)
        for ch in root.children:
            if ch.dep_ == "conj" and ch.pos_ in {"VERB", "AUX"}:
                preds.append(ch)

    return preds


# ============================================================
# EXTRACTION HELPERS
# ============================================================
def normalize_relation_from_verb(v) -> str:
    return safe_rel(v.lemma_.upper())


def get_subject_of_verb(v):
    for ch in v.children:
        if ch.dep_ in SUBJ_DEPS:
            return ch

    # If this verb is a conj, subject may be attached to the head
    if v.dep_ == "conj" and v.head is not None:
        for ch in v.head.children:
            if ch.dep_ in SUBJ_DEPS:
                return ch

    return None


def get_neg_mod_prefix(v) -> str:
    """Detect negation and modality prefixes for a verb."""
    neg = any(ch.dep_ == "neg" for ch in v.children)

    mod = ""
    for ch in v.children:
        if ch.dep_ == "aux" and ch.lemma_.lower() in {
            "may", "might", "can", "could", "must",
            "should", "would", "will", "shall"
        }:
            mod = ch.lemma_.upper() + "_"
            break

    pref = ""
    if neg:
        pref += "NOT_"
    if mod:
        pref += mod
    return pref


def objects_for_verb(v) -> List:
    """
    Return list of object head tokens for a verb:
    - direct objects / attrs / pobj via preps
    - expand conjunctions
    """
    objs = []

    for ch in v.children:
        if ch.dep_ in OBJ_DEPS and ch.pos_ != "PRON":
            objs.append(ch)

    for prep in v.children:
        if prep.dep_ == "prep":
            for gc in prep.children:
                if gc.dep_ == "pobj":
                    objs.append(gc)

    expanded = []
    for o in objs:
        expanded.append(o)
        for ch in o.children:
            if ch.dep_ == "conj":
                expanded.append(ch)

    uniq = []
    seen = set()
    for t in expanded:
        if t.i not in seen:
            seen.add(t.i)
            uniq.append(t)

    return uniq


def passive_agent_for_verb(v):
    """For passive voice: look for agent/by + pobj."""
    for ch in v.children:
        if ch.dep_ == "agent":
            for gc in ch.children:
                if gc.dep_ == "pobj":
                    return gc

    for ch in v.children:
        if ch.dep_ == "prep" and ch.lemma_.lower() == "by":
            for gc in ch.children:
                if gc.dep_ == "pobj":
                    return gc

    return None


# ============================================================
# COPULAR HANDLING (X is Y)
# ============================================================
def extract_copular_triples(sent_span, last_entity: Optional[str]) -> List[Triple]:
    """Handle: X is Y — copular clauses where ROOT is NOUN/ADJ with 'cop' child."""
    triples = []
    root = sent_span.root

    has_cop = any(ch.dep_ in COP_DEPS for ch in root.children)
    if not has_cop:
        return triples

    subj = None
    for ch in root.children:
        if ch.dep_ in SUBJ_DEPS:
            subj = ch
            break
    if subj is None:
        return triples

    # subject
    if subj.text.lower() in PRONOUNS and last_entity:
        s_text = last_entity
    else:
        s_text = noun_phrase_from_token(subj)

    if not is_good_entity(s_text):
        return triples

    # predicate complement is root itself
    o_text = noun_phrase_from_token(root)
    if not is_good_entity(o_text):
        return triples

    rel = "IS_A" if root.pos_ in {"NOUN", "PROPN"} else "IS"
    triples.append((clean_text(s_text), safe_rel(rel), clean_text(o_text)))
    return triples


# ============================================================
# RANGE FROM...TO HANDLING
# ============================================================
def extract_range_from_to(sent_span, subj_tok) -> List[Triple]:
    """Detect: 'ranging from X to Y' (or similar from/to patterns)."""
    triples = []
    root = sent_span.root

    if root.pos_ not in {"VERB", "AUX"}:
        return triples

    from_obj = None
    to_obj = None

    for prep in root.children:
        if prep.dep_ == "prep" and prep.lemma_.lower() == "from":
            for gc in prep.children:
                if gc.dep_ == "pobj":
                    from_obj = gc
        if prep.dep_ == "prep" and prep.lemma_.lower() == "to":
            for gc in prep.children:
                if gc.dep_ == "pobj":
                    to_obj = gc

    if not (from_obj or to_obj):
        return triples

    s_text = noun_phrase_from_token(subj_tok)
    if not is_good_entity(s_text):
        return triples

    if from_obj:
        o1 = noun_phrase_from_token(from_obj)
        if is_good_entity(o1):
            triples.append((clean_text(s_text), safe_rel("RANGE_FROM"), clean_text(o1)))

    if to_obj:
        o2 = noun_phrase_from_token(to_obj)
        if is_good_entity(o2):
            triples.append((clean_text(s_text), safe_rel("RANGE_TO"), clean_text(o2)))

    return triples


# ============================================================
# PRONOUN RESOLUTION (simple memory)
# ============================================================
def resolve_pronouns_with_memory(sentences: List[str]) -> List[str]:
    """Replace pronouns with the last known salient entity."""
    last_entity = None
    resolved = []

    for s in sentences:
        doc = nlp(s)

        words = []
        for tok in doc:
            if tok.text.lower() in PRONOUNS and last_entity:
                words.append(last_entity)
            else:
                words.append(tok.text)

        mem = pick_salient_entity(doc)
        if mem:
            last_entity = mem

        resolved.append(clean_ws(" ".join(words)))

    return resolved


# ============================================================
# MAIN TRIPLE EXTRACTOR (Span-safe)
# ============================================================
def extract_triples_from_sentences(sentences: List[str]) -> List[Triple]:
    """
    Extract S-R-O triples from a list of sentences.
    Uses pronoun memory across sentences for better resolution.
    """
    triples: List[Triple] = []
    last_entity: Optional[str] = None

    for sent in sentences:
        # Skip empty / punctuation-only lines
        if not sent or not re.search(r"[A-Za-z0-9]", sent):
            continue

        doc = nlp(sent)

        if len(doc) == 0:
            continue

        # IMPORTANT: use a Span to access .root
        # Because Doc has NO .root — only Span does
        sent_span = doc[:]

        # Update memory
        mem = pick_salient_entity(doc)
        if mem:
            last_entity = mem

        # Copular handling (X is Y)
        cop_tris = extract_copular_triples(sent_span, last_entity)
        if cop_tris:
            triples.extend(cop_tris)
            last_entity = cop_tris[0][0]
            continue

        preds = main_predicates(sent_span)
        if not preds:
            continue

        for v in preds:
            subj_tok = get_subject_of_verb(v)
            if subj_tok is None:
                continue

            # subject text (pronoun -> memory)
            if subj_tok.text.lower() in PRONOUNS and last_entity:
                subj_text = last_entity
            else:
                subj_text = noun_phrase_from_token(subj_tok)

            if not is_good_entity(subj_text):
                continue

            # Range detection only on the main sentence root
            if v == sent_span.root:
                triples.extend(extract_range_from_to(sent_span, subj_tok))

            # relation + neg/mod prefixes
            rel = normalize_relation_from_verb(v)
            rel = safe_rel(get_neg_mod_prefix(v) + rel)

            # Passive: if nsubjpass, use agent as object if present
            if subj_tok.dep_ == "nsubjpass":
                agent = passive_agent_for_verb(v)
                if agent is not None:
                    obj_text = noun_phrase_from_token(agent)
                    if is_good_entity(obj_text):
                        triples.append((clean_text(subj_text), rel, clean_text(obj_text)))
                        last_entity = clean_text(subj_text)
                        continue

            # Regular objects (with conj expansion)
            obj_toks = objects_for_verb(v)
            if not obj_toks:
                continue

            for o_tok in obj_toks:
                obj_text = noun_phrase_from_token(o_tok)
                if not is_good_entity(obj_text):
                    continue

                if clean_text(obj_text).lower() == clean_text(subj_text).lower():
                    continue

                triples.append((clean_text(subj_text), rel, clean_text(obj_text)))

            last_entity = clean_text(subj_text)

    # Ordered deduplication
    seen = set()
    uniq = []
    for t in triples:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


# ============================================================
# BACKWARD-COMPATIBLE API
# ============================================================
def extract_triples(text: str) -> List[Triple]:
    """
    Extract triples from a text string.
    This is the backward-compatible function called by pipeline.py.

    For single-sentence input (from pipeline chunks), processes directly.
    For multi-sentence input, splits and uses pronoun resolution.
    """
    doc = nlp(text)
    sentences = [s.text.strip() for s in doc.sents if s.text.strip()]

    if not sentences:
        return []

    return extract_triples_from_sentences(sentences)


# ============================================================
# FULL PIPELINE (for processing entire documents at once)
# ============================================================
def extract_triples_from_text(text: str) -> List[Triple]:
    """
    Full pipeline: split text → resolve pronouns → extract triples.
    Better for whole documents since pronoun resolution works across sentences.
    """
    doc = nlp(text)
    sentences = [s.text.strip() for s in doc.sents if s.text.strip()]

    if not sentences:
        return []

    # Resolve pronouns across sentences
    resolved = resolve_pronouns_with_memory(sentences)

    return extract_triples_from_sentences(resolved)


# ============================================================
# STANDALONE TEST
# ============================================================
if __name__ == "__main__":
    test_text = """
    Photosynthesis is a process used by plants. Plants convert sunlight into energy.
    They use carbon dioxide and water. Chlorophyll absorbs light, which is then
    converted into glucose and oxygen. The process occurs in the chloroplasts.
    Temperatures can range from 15 to 35 degrees Celsius.
    Plants do not require darkness for photosynthesis.
    """

    print("=" * 60)
    print("ENHANCED TRIPLE EXTRACTION TEST")
    print("=" * 60)

    triples = extract_triples_from_text(test_text)

    for i, (s, r, o) in enumerate(triples, 1):
        print(f"  {i}. ({s}, {r}, {o})")

    print(f"\nTotal triples: {len(triples)}")
    print("✓ Test complete!")