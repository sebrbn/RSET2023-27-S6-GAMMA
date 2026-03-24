import re
import nltk
from typing import List, Dict
from nltk.tokenize import sent_tokenize

# Setup NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

def resolve_pronouns(text: str) -> str:
    # (Your existing pronoun logic here...)
    return text 

def chunk_text(text: str, max_sentences: int = 4) -> List[str]:
    sentences = sent_tokenize(text)
    return [" ".join(sentences[i : i + max_sentences]) for i in range(0, len(sentences), max_sentences)]

class TripleExtractor:
    def __init__(self):
        self.patterns = [
            re.compile(r"([A-Z][\w\s]+)\s+(is|was|are|were|became)\s+([\w\s\.]+)"),
            re.compile(r"([A-Z][\w\s]+)\s+(discovered|launched|developed|created)\s+([\w\s\.]+)"),
        ]

    def extract(self, text: str) -> List[Dict[str, str]]:
        triples = []
        for sent in sent_tokenize(text):
            for pattern in self.patterns:
                match = pattern.search(sent)
                if match:
                    triples.append({
                        "subject": match.group(1).strip(),
                        "relation": match.group(2).strip(),
                        "object": match.group(3).strip().rstrip('.')
                    })
                    break
        return triples

def ingest_text(text: str):
    chunks = chunk_text(text)
    extractor = TripleExtractor()
    all_triples = []
    for chunk in chunks:
        all_triples.extend(extractor.extract(chunk))
        
    raw_bytes = len(text.encode('utf-8'))
    compressed_bytes = len(str(all_triples).encode('utf-8'))
    
    reduction = (1 - (compressed_bytes / raw_bytes)) * 100 if raw_bytes > 0 else 0

    return {
        "chunks": chunks,
        "triples": all_triples,
        "stats": {
            "raw_text_bytes": raw_bytes,
            "compressed_bytes": max(0, compressed_bytes),
            "percent_reduction": round(max(0, reduction), 2)
        }
    }