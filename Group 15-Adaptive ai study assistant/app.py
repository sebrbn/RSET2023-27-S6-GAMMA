"""
StudyAssist Backend — Flask + Groq API
Handles: file parsing, syllabus mapping, chunking, explanation generation
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, re, json, math, time, io, zipfile, hashlib
from werkzeug.utils import secure_filename
from collections import Counter
import groq

# ── Progress data store ──────────────────────────────────
# Stored in progress_data.json next to app.py
# Keyed by hashed API key so the real key is never stored
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), 'progress_data.json')

def _load_progress_store():
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_progress_store(store):
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(store, f, indent=2)
    except Exception as e:
        print(f"Progress save error: {e}")

def _key_hash(api_key: str) -> str:
    """Hash the API key — we never store the real key."""
    return hashlib.sha256(api_key.strip().encode()).hexdigest()[:24]

def get_progress(api_key: str) -> dict:
    store = _load_progress_store()
    uid   = _key_hash(api_key)
    return store.get(uid, {
        'studied':        [],
        'streak':         0,
        'last_study_day': None,
        'quiz_history':   {},   # "ModName::TopicName" -> [{score,total,pct,date}]
        'quizzes_taken':  0
    })

def save_progress(api_key: str, data: dict):
    store = _load_progress_store()
    uid   = _key_hash(api_key)
    store[uid] = data
    _save_progress_store(store)

app = Flask(__name__, static_folder='static', template_folder='.')
CORS(app)

# ════════════════════════════════════════════════
# FILE TEXT EXTRACTION
# ════════════════════════════════════════════════
def ocr_pdf(file_bytes: bytes) -> str:
    """
    OCR a scanned/image-based PDF using pdf2image + pytesseract.
    Called when normal text extraction returns empty or near-empty text.
    """
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
        from PIL import Image

        print("  OCR: converting PDF pages to images...")
        images = convert_from_bytes(
            file_bytes,
            dpi=200,           # 200 DPI — good balance of accuracy vs speed
            fmt='jpeg',
            thread_count=2
        )
        print(f"  OCR: running tesseract on {len(images)} pages...")
        pages_text = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang='eng')
            if text.strip():
                pages_text.append(f"[Page {i+1}]\n{text}")
            print(f"  OCR: page {i+1}/{len(images)} — {len(text)} chars")

        result = '\n\n'.join(pages_text)
        print(f"  OCR: total {len(result)} chars extracted")
        return result
    except Exception as e:
        print(f"  OCR failed: {e}")
        return ''


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from PDF, DOCX, or TXT file bytes.
    For PDFs: tries PyPDF2 → pdfplumber → OCR (for scanned/image PDFs).
    """
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'txt'

    if ext == 'pdf':
        text = ''

        # Method 1: PyPDF2
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            pages  = [p.extract_text() or '' for p in reader.pages]
            text   = '\n'.join(pages)
            print(f"  PyPDF2: {len(text)} chars from {len(reader.pages)} pages")
        except Exception as e:
            print(f"  PyPDF2 failed: {e}")

        # Method 2: pdfplumber (better for tables/complex layouts)
        if len(text.strip()) < 100:
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    pages = [p.extract_text() or '' for p in pdf.pages]
                text  = '\n'.join(pages)
                print(f"  pdfplumber: {len(text)} chars from {len(pages)} pages")
            except Exception as e:
                print(f"  pdfplumber failed: {e}")

        # Method 3: OCR — for scanned/image-based PDFs
        # Trigger if text is still suspiciously short (< 100 chars per page on average)
        try:
            import PyPDF2
            num_pages = len(PyPDF2.PdfReader(io.BytesIO(file_bytes)).pages)
        except Exception:
            num_pages = 1

        chars_per_page = len(text.strip()) / max(num_pages, 1)
        if chars_per_page < 100:
            print(f"  Low text density ({chars_per_page:.0f} chars/page) — trying OCR...")
            ocr_text = ocr_pdf(file_bytes)
            if len(ocr_text.strip()) > len(text.strip()):
                print(f"  OCR gave better result — using OCR text")
                text = ocr_text

        return text

    elif ext in ('docx', 'doc'):
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            print(f"docx failed: {e}")
            return ''

    elif ext == 'zip':
        try:
            combined = []
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                for name in zf.namelist():
                    # Skip hidden files, folders, __MACOSX junk
                    if name.startswith('__') or name.startswith('.') or name.endswith('/'):
                        continue
                    inner_ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
                    if inner_ext not in ('pdf', 'txt', 'docx', 'doc'):
                        continue
                    try:
                        inner_bytes = zf.read(name)
                        inner_text  = extract_text_from_file(inner_bytes, name)
                        if inner_text.strip():
                            combined.append(f"--- {name} ---\n{inner_text}")
                            print(f"  ZIP: extracted {name} ({len(inner_text)} chars)")
                    except Exception as e:
                        print(f"  ZIP: skipped {name} — {e}")
            return '\n\n'.join(combined)
        except Exception as e:
            print(f"ZIP extraction failed: {e}")
            return ''

    else:
        # Plain text — try UTF-8 then latin-1
        try:
            return file_bytes.decode('utf-8')
        except Exception:
            return file_bytes.decode('latin-1', errors='ignore')


GROQ_MODEL = "llama-3.3-70b-versatile"

# ════════════════════════════════════════════════
# TEXT CHUNKING
# ════════════════════════════════════════════════
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks for better context retrieval."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# ════════════════════════════════════════════════
# TF-IDF SIMILARITY (no external ML needed)
# ════════════════════════════════════════════════
def tokenize(text: str) -> list[str]:
    return re.findall(r'\b[a-z]{3,}\b', text.lower())

def tf(tokens: list[str]) -> dict:
    count = Counter(tokens)
    total = len(tokens) or 1
    return {t: c / total for t, c in count.items()}

def idf(word: str, all_docs: list[list[str]]) -> float:
    n = len(all_docs)
    df = sum(1 for doc in all_docs if word in doc)
    return math.log((n + 1) / (df + 1)) + 1

def tfidf_similarity(query: str, chunks: list[str]) -> list[tuple[float, str]]:
    q_tokens = tokenize(query)
    chunk_tokens = [tokenize(c) for c in chunks]
    all_docs = [q_tokens] + chunk_tokens
    vocab = set(q_tokens)

    q_tf = tf(q_tokens)
    scored = []
    for i, (chunk, c_tokens) in enumerate(zip(chunks, chunk_tokens)):
        c_tf = tf(c_tokens)
        score = sum(q_tf.get(w, 0) * c_tf.get(w, 0) * idf(w, all_docs) for w in vocab)
        scored.append((score, chunk))

    scored.sort(key=lambda x: -x[0])
    return scored


def find_relevant_chunks(topic: str, material_text: str, top_k: int = 7) -> tuple[str, float]:
    """Return most relevant chunks + confidence score (0-100)."""
    chunks = chunk_text(material_text)
    if not chunks:
        return "", 0
    
    scored = tfidf_similarity(topic, chunks)
    top_chunks = [c for _, c in scored[:top_k]]
    top_score = scored[0][0] if scored else 0

    # Normalize to 0-100 (heuristic)
    confidence = min(100, int(top_score * 8000))
    return '\n\n'.join(top_chunks), confidence


# ════════════════════════════════════════════════
# SYLLABUS PARSER — robust multi-format support
# ════════════════════════════════════════════════
def parse_syllabus(text: str) -> list[dict]:
    """
    Parse syllabus text into [{name, topics:[str]}].
    Handles: Unit/Module/Chapter headers, numbered sections,
    ALL-CAPS headings, Roman numerals, indented topics,
    bullet/dash lists, and plain line-by-line syllabuses.
    """
    lines = [l.rstrip() for l in text.split('\n') if l.strip()]
    if not lines:
        return [{'name': 'General Topics', 'topics': []}]

    # ── Pattern sets ──
    # Strong module headers: "Unit 1", "Module 2:", "Chapter III", "UNIT 1 -"
    strong_header = re.compile(
        r'^(unit|module|chapter|part|section|topic|block|semester)\s*[\dIVXivx]+[:\-–.]?\s*(.+)?',
        re.IGNORECASE
    )
    # Numbered section: "1.", "1.0", "1.1 Introduction" (but not "1.1.1" sub-sub)
    numbered_section = re.compile(r'^(\d+)\.(?!\d)\s*(.+)')
    # Sub-numbered topic: "1.1", "2.3 something"
    sub_numbered = re.compile(r'^\d+\.\d+[.\s]+(.+)')
    # Roman numeral header: "I.", "II.", "III."
    roman_header = re.compile(r'^(I{1,3}|IV|V?I{0,3}|IX|X{0,3})\.\s+(.+)', re.IGNORECASE)
    # Bullet/dash topic
    bullet = re.compile(r'^[\-*•►▸◆→]\s+(.+)')
    # ALL CAPS line (likely a section header if 3+ words or 10+ chars)
    def is_allcaps_header(line):
        clean = re.sub(r'[^a-zA-Z ]', '', line)
        return (len(clean) >= 8 and clean == clean.upper() and
                len(clean.split()) >= 2 and len(line) < 80)

    modules = []
    current = None
    pending_module_name = None

    def add_module(name):
        nonlocal current
        m = {'name': clean_line(name), 'topics': []}
        modules.append(m)
        current = m
        return m

    def add_topic(name):
        name = clean_line(name)
        if not name or len(name) < 3:
            return
        # Avoid adding duplicate of module name as first topic
        if current and name.lower() == current['name'].lower():
            return
        if current:
            current['topics'].append(name)

    def clean_line(s):
        # Remove leading numbers, bullets, colons
        s = re.sub(r'^[\d]+[:.\)]\s*', '', s.strip())
        s = re.sub(r'^[\-*•►▸◆→]\s*', '', s)
        return s.strip().strip(':').strip()

    for line in lines:
        stripped = line.strip()
        if not stripped or len(stripped) < 2:
            continue

        # ── Try strong header first ──
        m = strong_header.match(stripped)
        if m:
            name = m.group(2) or m.group(1)
            add_module(name.strip() or stripped)
            continue

        # ── Roman numeral header ──
        m = roman_header.match(stripped)
        if m:
            add_module(m.group(2))
            continue

        # ── ALL CAPS header ──
        if is_allcaps_header(stripped):
            add_module(stripped.title())
            continue

        # ── Numbered top-level section (e.g. "1. Introduction") ──
        m = numbered_section.match(stripped)
        if m:
            # Heuristic: if no modules yet or looks like a major section, make it a module
            name = m.group(2).strip()
            if not modules or (len(name) > 4 and not current):
                add_module(name)
            else:
                # Could be a topic under current module
                add_topic(name)
            continue

        # ── Sub-numbered topic (1.1, 2.3) — always a topic ──
        m = sub_numbered.match(stripped)
        if m:
            add_topic(m.group(1))
            continue

        # ── Bullet / dash ──
        m = bullet.match(stripped)
        if m:
            text_part = m.group(1).strip()
            # If no module yet, treat as module
            if not modules:
                add_module(text_part)
            else:
                add_topic(text_part)
            continue

        # ── Indented line = topic under current module ──
        if line.startswith(('  ', '\t')) and current:
            add_topic(stripped)
            continue

        # ── Plain line — heuristic: short lines = headers, longer = topics ──
        if not current:
            add_module(stripped)
        elif len(stripped) < 60 and len(stripped.split()) <= 8:
            # Could be a topic or a sub-header — add as topic
            add_topic(stripped)
        else:
            # Long line — likely descriptive, skip or add as topic
            if len(stripped.split()) <= 12:
                add_topic(stripped)

    # ── Post-processing ──
    # Remove modules with no topics — give them a default topic
    for mod in modules:
        if not mod['topics']:
            mod['topics'] = [mod['name'] + ' — Overview']

    # Merge very small modules (1 topic) into previous if too many
    if len(modules) > 20:
        merged = []
        for mod in modules:
            if merged and len(mod['topics']) <= 1 and len(merged[-1]['topics']) < 15:
                merged[-1]['topics'].extend(mod['topics'])
            else:
                merged.append(mod)
        modules = merged

    # Final fallback
    if not modules:
        # Split into chunks of 8 lines each as pseudo-modules
        chunk_size = 8
        for i in range(0, min(len(lines), 80), chunk_size):
            batch = lines[i:i+chunk_size]
            modules.append({
                'name': clean_line(batch[0]) if batch else f'Section {i//chunk_size+1}',
                'topics': [clean_line(l) for l in batch[1:] if len(l.strip()) > 3]
            })

    print(f"Parsed {len(modules)} modules from syllabus")
    for m in modules:
        print(f"  [{m['name']}] — {len(m['topics'])} topics")

    return modules


# ════════════════════════════════════════════════
# GROQ HELPERS
# ════════════════════════════════════════════════
def call_groq(api_key: str, prompt: str, max_tokens: int = 800) -> str:
    """Call Groq with auto-retry on rate limit."""
    client = groq.Groq(api_key=api_key)
    max_prompt_chars = 12000
    if len(prompt) > max_prompt_chars:
        prompt = prompt[:max_prompt_chars] + "\n...[trimmed for length]"

    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=max_tokens,
                temperature=0.6
            )
            return response.choices[0].message.content
        except Exception as e:
            msg = str(e)
            if '429' in msg or 'rate_limit' in msg.lower():
                wait = 15 * (attempt + 1)   # 15s, 30s, 45s, 60s, 75s
                print(f"Rate limited — waiting {wait}s before retry {attempt+1}/5")
                time.sleep(wait)
                continue
            raise
    raise Exception("Rate limit exceeded. Please wait 2-3 minutes and try again.")


# ════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')



@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Accept file upload and return extracted text."""
    file_type  = request.form.get('type', 'material')
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    f          = request.files['file']
    filename   = secure_filename(f.filename)
    file_bytes = f.read()

    print(f"\nUploading: {filename} ({len(file_bytes)//1024} KB)")
    text = extract_text_from_file(file_bytes, filename)

    if not text.strip():
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext == 'zip':
            return jsonify({'error': 'ZIP had no readable files. Ensure it contains PDF, DOCX, or TXT.'}), 400
        return jsonify({'error': f'Could not extract text from {filename}. File may be corrupted.'}), 400

    # Detect if OCR was used (text will contain [Page N] markers)
    ocr_used = '[Page 1]' in text

    return jsonify({
        'text':     text,
        'chars':    len(text),
        'filename': filename,
        'ocr_used': ocr_used,
        'pages':    text.count('[Page ')
    })


BULLET_CHARS = '\u2756\u2022\u25cf'  # ❖ • ●


def fix_pdf_words(text: str) -> str:
    """Fix word-splitting artifacts from PDF extraction (Kerala university PDFs)."""
    fixes = [
        (r'\bKno\s+wledge\b',          'Knowledge'),
        (r'\bkno\s+wledge\b',          'knowledge'),
        (r'\bRepr\s+esentation\b',     'Representation'),
        (r'\brepr\s+esentation\b',     'representation'),
        (r'\bAppr\s+oach(es)?\b',      lambda m: 'Approach' + (m.group(1) or '')),
        (r'\bappr\s+oach(es)?\b',      lambda m: 'approach' + (m.group(1) or '')),
        (r'\bPredicat\s+e[sd]?\b',     lambda m: 'Predicate' + m.group(0)[-1] if m.group(0)[-1] in 'sd' else 'Predicate'),
        (r'\bpredicat\s+e[sd]?\b',     lambda m: 'predicate' + m.group(0)[-1] if m.group(0)[-1] in 'sd' else 'predicate'),
        (r'\bNatur\s+al\b',            'Natural'),
        (r'\bnatur\s+al\b',            'natural'),
        (r'\bProcedur\s+al\b',         'Procedural'),
        (r'\bprocedur\s+al\b',         'procedural'),
        (r'\bDeclar\s+ative\b',        'Declarative'),
        (r'\bdeclar\s+ative\b',        'declarative'),
        (r'\bForw\s+ard\b',            'Forward'),
        (r'\bforw\s+ard\b',            'forward'),
        (r'\bBackw\s+ard\b',           'Backward'),
        (r'\bbackw\s+ard\b',           'backward'),
        (r'\bContr\s+ol\b',            'Control'),
        (r'\bcontr\s+ol\b',            'control'),
        (r'\bSear\s+ch(ing)?\b',       lambda m: 'Searching' if m.group(1) else 'Search'),
        (r'\bsear\s+ch(ing)?\b',       lambda m: 'searching' if m.group(1) else 'search'),
        (r'\bStructur\s+e\b',          'Structure'),
        (r'\bstructur\s+e\b',          'structure'),
        (r'\bG\s+ener\s*ative\b',      'Generative'),
        (r'\bGener\s+ative\b',         'Generative'),
        (r'\bgener\s+ative\b',         'generative'),
        (r'\bLanguag\s+e\b',           'Language'),
        (r'\blanguag\s+e\b',           'language'),
        (r'\bRepresent\s+ation\b',     'Representation'),
        (r'\brepresent\s+ation\b',     'representation'),
        (r'\bInferenc\s+e\b',          'Inference'),
        (r'\binferenc\s+e\b',          'inference'),
        (r'\bEnvironm\s+ent\b',        'Environment'),
        (r'\benvironm\s+ent\b',        'environment'),
        (r'\bAlgorithm\s+s\b',         'Algorithms'),
        (r'\bHeurist\s+ic\b',          'Heuristic'),
        (r'\bheurist\s+ic\b',          'heuristic'),
        (r'\bProbabilist\s+ic\b',      'Probabilistic'),
        (r'\bprobabilist\s+ic\b',      'probabilistic'),
        (r'\bClassif\s+ication\b',     'Classification'),
        (r'\bclassif\s+ication\b',     'classification'),
        (r'\bApplicat\s+ion[s]?\b',    lambda m: 'Applications' if m.group(0).endswith('s') else 'Application'),
        (r'\bapplicat\s+ion[s]?\b',    lambda m: 'applications' if m.group(0).endswith('s') else 'application'),
    ]
    for pattern, repl in fixes:
        if callable(repl):
            text = re.sub(pattern, repl, text)
        else:
            text = re.sub(pattern, repl, text)
    return text


def parse_flat_syllabus(text: str) -> list[dict]:
    """
    Parse syllabus PDFs. Handles all formats:
    - College: Module N: Title (N Hours) topic1, topic2, ...
    - School:  Ch-N / Chapter N / Unit N with bullet topics (* - bullet chars)
    - Spaced/broken text from bad PDF extraction
    """
    # Step 0: fix broken words FIRST before any parsing
    text = fix_pdf_words(text)

    # Step 1: collapse whitespace, insert newlines before bullet chars
    text = re.sub(r'\s+', ' ', text).strip()
    for ch in BULLET_CHARS:
        text = text.replace(ch, '\n' + ch)
    text = re.sub(r'\s+-\s+', '\n- ', text)
    text = re.sub(r'\s+\*\s+', '\n* ', text)

    # Step 2: detect format and split into per-module blocks
    has_module  = bool(re.search(r'Module\s+\d+',    text, re.IGNORECASE))
    has_chapter = bool(re.search(r'Chapter\s+\d+',   text, re.IGNORECASE))
    has_unit    = bool(re.search(r'Unit\s+\d+',      text, re.IGNORECASE))
    has_ch      = bool(re.search(r'Ch[-\u2013]\s*\d+', text))

    if has_module:
        splitter = re.compile(r'(?=Module\s+\d+\s*[:\-.]?\s)', re.IGNORECASE)
    elif has_chapter:
        splitter = re.compile(r'(?=Chapter\s+\d+[\s:.])', re.IGNORECASE)
    elif has_unit:
        splitter = re.compile(r'(?=Unit\s+\d+[\s:.])', re.IGNORECASE)
    elif has_ch:
        splitter = re.compile(r'(?=Ch[-\u2013]\s*\d+\s)')
    else:
        splitter = None

    blocks = [b.strip() for b in (splitter.split(text) if splitter else [text]) if b.strip()]

    noise_re = re.compile(
        r'(preamble|prerequisite|course code|b\.?\s*tech|rajagiri|kerala|india|www\.|'
        r'po\s*\d|pso\s*\d|co\s*\d|text\s*book|reference|evaluation|end\s*semester|'
        r'semester\s+[ivx\d]|credit|l\s+t\s+p|year of introduction|programme outcome|'
        r'directorate|gnct|annual syllabus|learning outcome|mid.?term|revision|'
        r'worksheet|activities|experiment)',
        re.IGNORECASE
    )
    header_re = re.compile(r'^(?:Module|Chapter|Unit|Ch[-\u2013]?)\s*\d+\s*[:\-\u2013.]?\s*', re.IGNORECASE)
    hours_re  = re.compile(r'\(\d+\s*Hours?\)', re.IGNORECASE)
    bullet_re = re.compile(r'^[' + BULLET_CHARS + r'\-\*]\s*(.+)')

    modules = []

    for block in blocks:
        if noise_re.search(block[:80]):
            continue

        lines_b = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines_b:
            continue

        # Extract name from first (header) line
        header_line = lines_b[0]
        after_header = header_re.sub('', header_line).strip()

        hours_match = hours_re.search(after_header)
        if hours_match:
            # College format: name is before the "(N Hours)" marker
            hours_pos = after_header.find(hours_match.group(0))
            name = after_header[:hours_pos].strip().strip(':-').strip()
            inline_rest = after_header[hours_pos + len(hours_match.group(0)):].strip().lstrip('.,').strip()
        else:
            after_header = hours_re.sub('', after_header).strip()
            nm = re.match(r'^([^,\n]{3,60})', after_header)
            name = nm.group(1).strip().strip(':-').strip() if nm else after_header[:50].strip()
            inline_rest = after_header[len(name):].strip().lstrip('.,').strip() if nm else ''

        name = re.sub(r'\s+', ' ', name).strip()
        if not name or len(name) < 2:
            continue

        topics = []

        # School format: bullet lines after header
        bullet_lines = [l for l in lines_b[1:] if bullet_re.match(l)]
        if bullet_lines:
            for l in bullet_lines:
                t = bullet_re.match(l).group(1).strip().rstrip('.')
                t = hours_re.sub('', t).strip()
                if len(t) > 3 and not noise_re.search(t):
                    topics.append(t)

        # College format: comma-separated topics after hours marker
        if inline_rest:
            for t in re.split(r',', inline_rest):  # only comma, not period
                t = re.sub(r'\s+', ' ', t.strip().strip(':-').strip())
                # Skip if it looks like a sentence (has multiple words forming prose)
                if 4 <= len(t) <= 80 and not noise_re.search(t) and not re.match(r'^\d+$', t):
                    if t not in topics:
                        topics.append(t)

        # College format: non-bullet continuation lines
        non_bullet_lines = [l for l in lines_b[1:] if not bullet_re.match(l) and len(l) > 10]
        if not bullet_lines and non_bullet_lines:
            for l in non_bullet_lines:
                if noise_re.search(l):
                    continue
                # Only split on commas (not periods) to avoid splitting sentences
                for t in re.split(r',', l):
                    t = re.sub(r'\s+', ' ', t.strip().strip(':-').strip())
                    if 4 <= len(t) <= 80 and not noise_re.search(t) and not re.match(r'^\d+$', t):
                        if t not in topics:
                            topics.append(t)

        # Cap topics to avoid runaway parsing (Module 6 "Applications" issue)
        topics = topics[:20]

        if not topics:
            topics = [name + ' — Overview']

        modules.append({'name': name, 'topics': topics})

    return modules




@app.route('/api/parse-syllabus', methods=['POST'])
def api_parse_syllabus():
    """Parse uploaded syllabus into clean chapter modules."""
    data          = request.json
    syllabus_text = data.get('syllabus_text', '')
    api_key       = data.get('api_key', '')

    if not syllabus_text:
        return jsonify({'error': 'No syllabus text provided'}), 400

    # Step 1: flat-line parser (handles PDFs where text has no newlines)
    modules = parse_flat_syllabus(syllabus_text)
    total   = sum(len(m['topics']) for m in modules)
    print(f"Flat parser: {len(modules)} modules, {total} topics")

    # Step 2: rule-based if flat failed
    if len(modules) < 2 or total < 3:
        print("Flat parser insufficient, trying rule-based...")
        modules = parse_syllabus(syllabus_text)
        total   = sum(len(m['topics']) for m in modules)
        print(f"Rule-based: {len(modules)} modules, {total} topics")

    # Final step: clean all module names and topic names with word-fixer
    for m in modules:
        m['name'] = fix_pdf_words(m['name'])
        m['topics'] = [fix_pdf_words(t) if isinstance(t, str) else fix_pdf_words(t.get('name','')) for t in m['topics']]
        # Normalize topics to {name} objects if they are strings
        m['topics'] = [{'name': t} if isinstance(t, str) else t for t in m['topics']]
    if api_key and (len(modules) < 2 or total < 3):
        print("Both parsers failed, trying Groq...")
        try:
            clean_text = re.sub(r'\s+(Ch[-\u2013\s]*\d+)', r'\n\1', syllabus_text)
            clean_text = re.sub(r'([\u2756\u2022\u25cf])', r'\n\1', clean_text)
            clean_text = re.sub(r'  +', '\n', clean_text)
            prompt = (
                "Extract chapters and topics from this school syllabus.\n"
                "Ch-1, Ch-2 etc mark chapter starts. Lines with ❖ or • are topics.\n"
                "Ignore school name, dates, learning outcomes, worksheets.\n\n"
                "TEXT:\n---\n" + clean_text[:3500] + "\n---\n\n"
                "Return ONLY JSON:\n"
                '[{"name": "Chapter title", "topics": ["topic 1", "topic 2"]}]'
            )
            raw = call_groq(api_key, prompt, max_tokens=1200)
            jm  = re.search(r'\[[\s\S]*\]', raw)
            if jm:
                groq_mods = json.loads(jm.group(0))
                skip = ['directorate','gnct','annual','worksheet','suggestive',
                        'mapping','mid term','examination','revision','theme']
                groq_clean = [
                    {'name': m['name'],
                     'topics': [t for t in m.get('topics', []) if len(t) > 3]}
                    for m in groq_mods
                    if not any(s in m.get('name','').lower() for s in skip)
                    and m.get('topics')
                ]
                if len(groq_clean) >= 2:
                    modules = groq_clean
                    print(f"Groq gave {len(modules)} modules")
        except Exception as e:
            print(f"Groq failed: {e}")

    print(f"FINAL: {len(modules)} modules, {sum(len(m['topics']) for m in modules)} topics")
    for m in modules:
        print(f"  [{m['name']}]: {m['topics']}")
    return jsonify({'modules': modules})


@app.route('/api/explain', methods=['POST'])
def api_explain():
    """Generate topic explanation with confidence score."""
    data = request.json
    api_key   = data.get('api_key', '')
    topic     = data.get('topic', '')
    module    = data.get('module', '')
    material  = data.get('material_text', '')
    syllabus  = data.get('syllabus_text', '')
    level     = data.get('level', 'beginner')
    student   = data.get('student_type', 'school')

    if not topic:
        return jsonify({'error': 'No topic specified'}), 400

    if not api_key:
        return jsonify({
            'explanation': f"### Demo Mode\n\nYou are viewing a demo explanation for **{topic}** (module: {module}).\n\nTo get real AI-generated explanations from your study material, please enter your Groq API key on the upload page.\n\n### Key Takeaways\n- Add your Groq API key to unlock full explanations\n- Get a free key at console.groq.com",
            'confidence': 50,
            'chunks_used': 0
        })

    # Retrieve relevant chunks from material using TF-IDF
    search_text = material or syllabus
    context, confidence = find_relevant_chunks(topic + ' ' + module, search_text) if search_text else ('', 30)

    level_map = {
        ('school',  'beginner'):     ('a school student seeing this topic for the first time (age 12-14)',
                                      'Use the simplest possible language. Define every term. Use one real-life analogy. Keep it short and friendly. No formulas unless absolutely necessary.'),
        ('school',  'intermediate'): ('a school student who has heard of this topic before (age 14-16)',
                                      'Go one level deeper. Explain how and why, not just what. Include 1-2 examples. Introduce basic technical terms with definitions.'),
        ('school',  'advanced'):     ('a high-achieving school student preparing for board/competitive exams',
                                      'Be thorough and precise. Cover edge cases, exceptions, and applications. Use correct technical terminology. Include a comparison or contrast where applicable.'),
        ('college', 'beginner'):     ('a first-year college student new to this topic',
                                      'Build from first principles. Define concepts clearly before using them. Use relatable examples. Avoid assuming prior knowledge.'),
        ('college', 'intermediate'): ('a college student with foundational knowledge of this subject',
                                      'Use technical language freely. Go into mechanisms and reasoning. Include real-world or industry applications. Reference related concepts.'),
        ('college', 'advanced'):     ('an advanced college student or exam topper preparing for competitive exams',
                                      'Be academically rigorous. Cover theory deeply, discuss limitations, compare approaches, and mention current relevance or research context.'),
    }
    key = (student, level)
    audience, instructions = level_map.get(key, ('a student', 'Explain clearly with examples.'))
    level_desc = audience

    has_context = bool(context.strip())
    if has_context:
        context_section = f"The following is extracted DIRECTLY from the student's own study material. You MUST base your explanation on this text. Do not make up information not present here:\n---\n{context[:4000]}\n---"
    else:
        context_section = "No study material was provided. Use your general knowledge to explain this topic accurately."

    material_instruction = (
        "Your explanation MUST be grounded in the provided study material above. "
        "Quote or closely paraphrase specific details, definitions, examples, and facts from it. "
        "If the material covers this topic, do NOT invent information — use what is there."
    ) if has_context else (
        "No study material provided. Use accurate general knowledge."
    )

    prompt = f"""You are a study assistant helping {audience}.

TOPIC: "{topic}"
MODULE: "{module}"

{context_section}

INSTRUCTIONS FOR THIS LEVEL:
{instructions}

{material_instruction}

Write a thorough, well-structured explanation with ALL of these sections:

### Overview
Write 3-4 sentences introducing "{topic}". Start with a clear definition. Mention its importance or relevance.

### Key Concepts
Cover every important idea within "{topic}". For each concept:
- Give a clear definition or explanation
- Add a sub-point with detail or mechanism
- Use specific facts, numbers, or terms from the material if available
Aim for at least 4-5 distinct concepts.

### How It Works
Explain the process, mechanism, or steps involved in detail. Use numbered steps if it is a process. Be thorough — 4-6 sentences minimum.

### Real-World Examples
Give 2-3 concrete examples or applications. Make them specific and relatable. Prefer examples from the study material if present.

### Common Mistakes / Things to Remember
List 3-4 bullet points of things students often confuse or forget about this topic.

IMPORTANT: Be thorough and detailed. Each section should have substantial content — do not give one-line answers. Use the study material facts wherever possible."""

    # Debug: print context quality
    print(f"  Explain '{topic}': context={len(context)} chars, confidence={confidence}")
    print(f"  First 200 chars of context: {context[:200]!r}")

    try:
        text = call_groq(api_key, prompt, max_tokens=2000)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    clean_text = re.sub(r'CONFIDENCE_SCORE:\s*\d+', '', text).strip()

    return jsonify({
        'explanation': clean_text,
        'confidence': confidence,
        'chunks_used': len(context.split()) if context else 0
    })


@app.route('/api/questions', methods=['POST'])
def api_questions():
    """Generate MCQ questions for a topic."""
    data = request.json
    api_key  = data.get('api_key', '')
    topic    = data.get('topic', '')
    module   = data.get('module', '')
    student  = data.get('student_type', 'school')
    level    = data.get('level', 'beginner')
    material = data.get('material_text', '')
    syllabus = data.get('syllabus_text', '')
    count    = 8  # number of MCQs

    search_text = material or syllabus
    context, _ = find_relevant_chunks(topic + ' ' + module, search_text) if search_text else ('', 0)

    if context.strip():
        context_section = f"""STUDY MATERIAL CONTEXT (use this as the basis for questions):
---
{context[:4000]}
---"""
    else:
        context_section = "No study material provided — use your general academic knowledge about this topic."

    difficulty_map = {
        'beginner':     'Easy — definitions, simple recall, basic identification. Questions like "What is X?" or "Which of these defines Y?"',
        'intermediate': 'Medium — application and understanding. Questions like "Why does X happen?" or "Which best explains Y?"',
        'advanced':     'Hard — analysis and application. Scenario-based questions, compare/contrast, cause-effect relationships.',
    }
    difficulty_instruction = difficulty_map.get(level, 'Mix of easy and medium questions.')

    prompt = f"""You are a {student} exam question generator. Generate exactly {count} MCQ questions SPECIFICALLY about "{topic}".

TOPIC TO TEST: "{topic}"
MODULE: "{module}"
STUDENT LEVEL: {student}, {level}

{context_section}

STRICT RULES:
1. Every single question MUST be specifically about "{topic}" — not about the study material in general, not about other topics
2. NEVER ask "What is the main topic of the provided material?" or any meta-question about the document
3. NEVER ask "According to the text..." or "What does the material say..." — ask about the actual subject matter
4. Questions must test knowledge OF "{topic}" itself — its concepts, definitions, mechanisms, examples
5. All 4 options must be plausible — no obviously silly wrong answers
6. Difficulty: {difficulty_instruction}

Return ONLY a valid JSON array, no extra text, no markdown:
[
  {{
    "question": "A specific question about {topic}?",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "A",
    "explanation": "Why this answer is correct"
  }}
]"""

    if not api_key:
        return jsonify({'questions': _demo_mcqs(topic, count)})

    try:
        text = call_groq(api_key, prompt, max_tokens=1500)
        json_match = re.search(r'\[[\s\S]*\]', text)
        questions = json.loads(json_match.group(0)) if json_match else []
        if not questions:
            raise Exception("No valid JSON returned from AI")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'questions': questions})


@app.route('/api/search', methods=['POST'])
def api_search():
    """Search material text and return matching topic/module."""
    data = request.json
    query    = data.get('query', '').strip()
    material = data.get('material_text', '')
    syllabus = data.get('syllabus_text', '')
    modules  = data.get('modules', [])

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    results = []

    # Search through module/topic names first
    query_lower = query.lower()
    for mi, mod in enumerate(modules):
        # Check module name
        if query_lower in mod.get('name', '').lower():
            results.append({
                'type': 'module',
                'module_idx': mi,
                'topic_idx': 0,
                'module_name': mod['name'],
                'topic_name': mod['topics'][0] if mod.get('topics') else '',
                'preview': f"Module: {mod['name']}",
                'score': 1.0
            })
        # Check topic names
        for ti, topic in enumerate(mod.get('topics', [])):
            tname = topic if isinstance(topic, str) else topic.get('name', '')
            if query_lower in tname.lower():
                results.append({
                    'type': 'topic',
                    'module_idx': mi,
                    'topic_idx': ti,
                    'module_name': mod['name'],
                    'topic_name': tname,
                    'preview': f"{mod['name']} → {tname}",
                    'score': 0.9
                })

    # Also do TF-IDF search on material content
    search_text = material or syllabus
    if search_text and not results:
        chunks = chunk_text(search_text)
        scored = tfidf_similarity(query, chunks)
        for score, chunk in scored[:3]:
            if score > 0:
                # Try to match chunk back to a topic
                for mi, mod in enumerate(modules):
                    for ti, topic in enumerate(mod.get('topics', [])):
                        tname = topic if isinstance(topic, str) else topic.get('name', '')
                        if any(w in chunk.lower() for w in tname.lower().split()[:3]):
                            results.append({
                                'type': 'content',
                                'module_idx': mi,
                                'topic_idx': ti,
                                'module_name': mod['name'],
                                'topic_name': tname,
                                'preview': chunk[:120] + '...',
                                'score': round(score, 4)
                            })
                            break

    # Deduplicate by module_idx + topic_idx
    seen = set()
    unique = []
    for r in results:
        key = (r['module_idx'], r['topic_idx'])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return jsonify({'results': unique[:6]})


def _demo_mcqs(topic, count=8):
    return [
        {
            "question": f"Which of the following best defines {topic}?",
            "options": {"A": f"A core concept in the study of {topic}", "B": "An unrelated term", "C": "A mathematical formula only", "D": "None of the above"},
            "answer": "A",
            "explanation": f"{topic} is indeed a core concept in its subject area."
        },
        {
            "question": f"What is the primary purpose of {topic}?",
            "options": {"A": "To confuse students", "B": "To explain natural phenomena", "C": "To replace mathematics", "D": "To describe history only"},
            "answer": "B",
            "explanation": "Add your Groq API key to get questions from your actual study material."
        }
    ] * (count // 2)


@app.route('/api/debug-mapping', methods=['POST'])
def api_debug_mapping():
    """Shows chunking + mapping results — useful for project demonstration."""
    data = request.json
    material  = data.get('material_text', '')
    syllabus  = data.get('syllabus_text', '')
    topic     = data.get('topic', '')

    search_text = material or syllabus
    if not search_text:
        return jsonify({'error': 'No material provided'}), 400

    # Step 1: Chunking
    chunks = chunk_text(search_text)

    # Step 2: TF-IDF scoring for the topic
    scored = tfidf_similarity(topic, chunks) if topic else [(0, c) for c in chunks]

    # Step 3: Return detailed breakdown
    results = []
    for score, chunk in scored[:5]:
        results.append({
            'score':      round(score, 6),
            'word_count': len(chunk.split()),
            'preview':    chunk[:200] + ('...' if len(chunk) > 200 else '')
        })

    return jsonify({
        'topic':         topic,
        'total_chunks':  len(chunks),
        'total_words':   len(search_text.split()),
        'chunk_size':    800,
        'overlap':       100,
        'top_matches':   results,
        'best_score':    round(scored[0][0], 6) if scored else 0,
        'confidence':    min(100, int(scored[0][0] * 8000)) if scored else 0
    })




@app.route('/api/debug-text', methods=['POST'])
def api_debug_text():
    """Return raw extracted text for debugging."""
    data = request.json
    syllabus = data.get('syllabus_text', '')
    material = data.get('material_text', '')
    # Show first 2000 chars of each
    return jsonify({
        'syllabus_raw': syllabus[:2000],
        'syllabus_len': len(syllabus),
        'material_raw': material[:500],
        'material_len': len(material)
    })


@app.route('/api/progress/load', methods=['POST'])
def api_progress_load():
    """Load saved progress for this API key."""
    data    = request.json
    api_key = data.get('api_key', '').strip()
    if not api_key:
        return jsonify({'error': 'No API key'}), 400
    progress = get_progress(api_key)
    return jsonify(progress)


@app.route('/api/progress/save', methods=['POST'])
def api_progress_save():
    """Save progress for this API key."""
    data    = request.json
    api_key = data.get('api_key', '').strip()
    if not api_key:
        return jsonify({'error': 'No API key'}), 400
    progress = data.get('progress', {})

    # Update streak logic on the server side
    from datetime import date
    today     = date.today().isoformat()          # "2024-03-15"
    yesterday = (date.today().replace(day=date.today().day - 1) if date.today().day > 1
                 else date.today()).isoformat()

    last_day = progress.get('last_study_day')
    streak   = progress.get('streak', 0)

    if last_day != today:
        # Check if yesterday — continue streak; otherwise reset to 1
        from datetime import date, timedelta
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()
        if last_day == yesterday_str:
            progress['streak'] = streak + 1
        elif last_day is None:
            progress['streak'] = 1
        else:
            progress['streak'] = 1   # gap in days — reset streak
        progress['last_study_day'] = today

    save_progress(api_key, progress)
    return jsonify({'ok': True, 'streak': progress.get('streak', 0)})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat with notes — RAG-based Q&A over uploaded material."""
    data     = request.json
    api_key  = data.get('api_key', '')
    question = data.get('question', '').strip()
    material = data.get('material_text', '')
    syllabus = data.get('syllabus_text', '')
    history  = data.get('history', [])

    if not question:
        return jsonify({'error': 'No question provided'}), 400
    if not api_key:
        return jsonify({'answer': 'Please enter your Groq API key to use chat.'}), 200

    # Retrieve relevant context — search both material AND syllabus
    # Use larger top_k and bigger context window for chat
    context = ''
    confidence = 0
    search_text = material or syllabus
    if search_text:
        context, confidence = find_relevant_chunks(question, search_text, top_k=8)

    # Check if the context is actually relevant to the question
    # by seeing if key question words appear in it
    q_words = set(w.lower() for w in question.split() if len(w) > 3)
    context_words = set(w.lower() for w in context.split())
    overlap = q_words & context_words
    material_is_relevant = len(overlap) >= 2 and confidence > 0

    print(f"  Chat Q: '{question[:60]}' | context={len(context)} chars | relevant={material_is_relevant} | overlap={overlap}")

    # Build conversation history
    history_str = ''
    for turn in history[-6:]:
        role = 'Student' if turn['role'] == 'user' else 'Assistant'
        history_str += f"{role}: {turn['content']}\n"

    if material_is_relevant:
        context_block = (
            f"Relevant excerpts from the student's study material:\n---\n{context[:4000]}\n---\n\n"
        )
        material_instruction = (
            "First check if the answer is in the material above.\n"
            "If yes — answer using the material, mentioning specific facts from it.\n"
            "If the material only partially covers it — use the material as a base and supplement with your knowledge.\n"
            "NEVER say 'the material does not discuss this' — always give a complete helpful answer."
        )
    else:
        context_block = ""
        material_instruction = (
            "The uploaded material doesn't seem to cover this specific question directly.\n"
            "Give a thorough, accurate answer from your general knowledge.\n"
            "Be specific and educational — explain concepts clearly with examples."
        )

    prompt = (
        "You are a friendly, knowledgeable study assistant for a student.\n"
        "Your job is to ALWAYS give a complete, helpful answer — never leave the student without information.\n\n"
        + context_block
        + material_instruction + "\n\n"
        + (f"Previous conversation:\n{history_str}\n" if history_str else "")
        + f"Student: {question}\n\nAssistant:"
    )

    try:
        answer = call_groq(api_key, prompt, max_tokens=800)
        return jsonify({'answer': answer.strip(), 'confidence': confidence})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    try:
        answer = call_groq(api_key, prompt, max_tokens=600)
        return jsonify({'answer': answer.strip(), 'confidence': confidence})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/weightage', methods=['POST'])
def api_weightage():
    """Analyse exam weightage for all topics in a module using Groq."""
    data      = request.json
    api_key   = data.get('api_key', '')
    modules   = data.get('modules', [])   # [{name, topics:[{name}]}]
    syllabus  = data.get('syllabus_text', '')
    material  = data.get('material_text', '')

    if not api_key:
        return jsonify({'error': 'No API key'}), 400
    if not modules:
        return jsonify({'error': 'No modules provided'}), 400

    # Build a flat topic list with module context
    all_topics = []
    for mod in modules:
        for t in mod.get('topics', []):
            name = t if isinstance(t, str) else t.get('name', '')
            if name:
                all_topics.append({'module': mod['name'], 'topic': name})

    if not all_topics:
        return jsonify({'error': 'No topics found'}), 400

    # Build context from syllabus (more relevant for weightage than full textbook)
    context = (syllabus[:3000] if syllabus.strip()
               else material[:2000] if material.strip()
               else '')

    topic_list_str = '\n'.join(
        f'- [{t["module"]}] {t["topic"]}' for t in all_topics
    )

    prompt = f"""You are an expert academic consultant. Analyse the exam weightage of each topic below.

CONTEXT (syllabus/material):
---
{context[:2000] if context else 'No syllabus provided — use general academic knowledge.'}
---

TOPICS TO ANALYSE:
{topic_list_str}

For each topic, assign exam weightage based on:
- How frequently it appears in exams
- How fundamental it is to the subject
- How much syllabus coverage it gets
- Whether it is typically a high-mark question topic

Respond ONLY with a valid JSON array. No explanation, no markdown, no backticks.
Each item must have exactly these fields:
- "module": the module name exactly as given
- "topic": the topic name exactly as given
- "weightage": one of "high", "medium", or "low"
- "reason": one short sentence explaining why (max 10 words)

Example format:
[{{"module":"Physics","topic":"Newton Laws","weightage":"high","reason":"Fundamental concept tested in every exam"}},...]

Now output the JSON array for all {len(all_topics)} topics:"""

    try:
        raw = call_groq(api_key, prompt, max_tokens=2000)
        # Parse JSON from response
        raw = raw.strip()
        # Strip markdown code fences if present
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        # Find the JSON array
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            raw = match.group(0)
        result = json.loads(raw)
        return jsonify({'weightage': result})
    except json.JSONDecodeError as e:
        print(f"Weightage JSON parse error: {e}\nRaw: {raw[:300]}")
        return jsonify({'error': 'Could not parse weightage response'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n🎓 StudyAssist backend starting...")
    print("📂 Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)
