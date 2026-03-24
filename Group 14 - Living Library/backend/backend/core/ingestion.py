import spacy

nlp = spacy.load("en_core_web_sm")


def ingest_text(text: str):
    """
    Splits input text into sentence chunks.
    Returns a dictionary with a list of chunks.
    """

    doc = nlp(text)

    chunks = []

    for sent in doc.sents:
        cleaned = sent.text.strip()

        if cleaned:
            chunks.append(cleaned)

    return {
        "chunks": chunks
    }