# ---------------------------------------------------
# UNIVERSAL RESUME PARSER (TEXT + SCANNED + IMAGE)
# ---------------------------------------------------

import os
import re
import fitz  # PyMuPDF
import pytesseract

from PIL import Image
from nltk.tokenize import sent_tokenize

from services.skill_ontology import SKILL_ONTOLOGY
from services.semantic_engine import normalize_skills
from services.embedding_matcher import detect_semantic_skills
from datetime import datetime


# ---------------------------------------------------
# TESSERACT PATH (Windows)
# ---------------------------------------------------
pytesseract.pytesseract.tesseract_cmd = \
r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------------------------------------------------
# 1️⃣ TEXT PDF EXTRACTION
# ---------------------------------------------------
def extract_text_from_pdf(file_path):

    text = ""

    pdf = fitz.open(file_path)

    for page in pdf:
        text += page.get_text()

    return text


# ---------------------------------------------------
# 2️⃣ OCR EXTRACTION (PDF → IMAGE → TEXT)
# ---------------------------------------------------
def extract_text_using_ocr(file_path):

    print("⚠️ OCR FALLBACK ACTIVATED")

    text = ""

    pdf = fitz.open(file_path)

    for page in pdf:

        pix = page.get_pixmap(dpi=300)

        img = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        text += pytesseract.image_to_string(img)

    return text


# ---------------------------------------------------
# 3️⃣ IMAGE RESUME OCR
# ---------------------------------------------------
def extract_text_from_image(file_path):

    print("🖼️ IMAGE OCR ACTIVATED")

    img = Image.open(file_path)

    text = pytesseract.image_to_string(img)

    return text


# ---------------------------------------------------
# 4️⃣ CLEAN TEXT
# ---------------------------------------------------
def clean_text(text):

    text = text.lower()
    text = re.sub(r'\s+', ' ', text)

    return text


# ---------------------------------------------------
# 5️⃣ BUILD SKILL DATABASE
# ---------------------------------------------------
def build_skill_database():

    skill_db = []

    for role in SKILL_ONTOLOGY.values():

        for category in role.values():

            skill_db.extend(category)

    return list(set(skill_db))


# ---------------------------------------------------
# 6️⃣ KEYWORD SKILL MATCH
# ---------------------------------------------------
def extract_keyword_skills(sentences):

    skill_db = build_skill_database()

    found = []

    for sentence in sentences:

        for skill in skill_db:

            if skill.lower() in sentence:
                found.append(skill)

    return list(set(found))


# ---------------------------------------------------
# 7️⃣ EXPERIENCE EXTRACTION
# ---------------------------------------------------
def extract_experience(text):

    import re
    from datetime import datetime

    text = text.lower()
    current_year = datetime.now().year
    current_month = datetime.now().month

    # -----------------------------
    # isolate EXPERIENCE section
    # -----------------------------
    if "experience" in text:
        text = text.split("experience",1)[1]

    for stop in [
        "projects","education","skills",
        "leadership","awards","references"
    ]:
        if stop in text:
            text = text.split(stop,1)[0]

    # -----------------------------
    # month mapping
    # -----------------------------
    months = {
        "jan":1,"feb":2,"mar":3,"apr":4,
        "may":5,"jun":6,"jul":7,"aug":8,
        "sep":9,"sept":9, "oct":10,"nov":11,"dec":12
    }

    total_months = 0
    seen = set()

    # -----------------------------
    # Pattern 1: Month-Year ranges
    # -----------------------------
    pattern = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(\d{4})\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present|current)[a-z]*\s*(\d{4})?'

    matches = re.findall(pattern,text)

    print("Month Pattern matches",matches)

    for sm,sy,em,ey in matches:

        start_month = months[sm[:3]]
        start_year = int(sy)

        if em in ["present","current"]:
            end_month = current_month
            end_year = current_year
        else:
            end_month = months[em[:3]]
            end_year = int(ey)

        key=(start_year,start_month,end_year,end_month)

        if key in seen:
            continue

        seen.add(key)

        months_worked=(end_year-start_year)*12+(end_month-start_month)

        if months_worked>0:
            total_months+=months_worked

    # -----------------------------
    # Pattern 2: Year-only ranges
    # -----------------------------
    pattern_year = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'

    matches = re.findall(pattern_year,text)

    print("Month pattern matches:", matches)

    for sy,ey in matches:

        start_year = int(sy)

        if ey in ["present","current"]:
            end_year = current_year
        else:
            end_year = int(ey)

        months_worked = (end_year-start_year)*12

        if months_worked>0:
            total_months += months_worked

    return round(total_months/12,1)
# ---------------------------------------------------
# 8️⃣ MASTER PARSER
# ---------------------------------------------------
def parse_resume(file_path, role=None):

    print("\n========== PARSER START ==========")
    print("File:", file_path)

    ext = file_path.split(".")[-1].lower()

    # ---------------------------------------------------
    # STEP 1 — TEXT EXTRACTION
    # ---------------------------------------------------
    if ext == "pdf":

        raw_text = extract_text_from_pdf(file_path)

        print("PDF TEXT LENGTH:", len(raw_text))

        # OCR fallback if empty
        if len(raw_text.strip()) < 50:

            raw_text = extract_text_using_ocr(file_path)

    elif ext in ["png", "jpg", "jpeg"]:

        raw_text = extract_text_from_image(file_path)

    else:
        raw_text = ""

    print("FINAL TEXT LENGTH:", len(raw_text))

    if len(raw_text.strip()) == 0:

        print("❌ NO TEXT EXTRACTED")
        return {
            "skills": [],
            "experience": 0
        }

    # ---------------------------------------------------
    # STEP 2 — CLEAN
    # ---------------------------------------------------
    cleaned = clean_text(raw_text)

    # ---------------------------------------------------
    # STEP 3 — SENTENCE TOKENIZE
    # ---------------------------------------------------
    sentences = sent_tokenize(cleaned)

    # ---------------------------------------------------
    # STEP 4 — SKILL EXTRACTION
    # ---------------------------------------------------
    keyword_skills = extract_keyword_skills(sentences)

    semantic_skills = detect_semantic_skills(sentences)

    combined = list(set(keyword_skills + semantic_skills))

    normalized = normalize_skills(combined)

    print("SKILLS FOUND:", normalized)

    # ---------------------------------------------------
    # STEP 5 — EXPERIENCE
    # ---------------------------------------------------
    experience = extract_experience(cleaned)

    print("EXPERIENCE:", experience)

    print("========== PARSER END ==========\n")

    return {

        "skills": normalized,
        "experience": experience
    }
