# 🎓 StudyAssist — AI-Powered Study Companion

> Upload your textbook and syllabus → get smart explanations, topic mapping, and exam questions tailored to your level.

---

## 🗂 Project Structure

```
studyassist/
├── index.html          ← Full frontend (single file, no build needed)
├── app.py              ← Flask backend (API routes, Groq integration)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Student Type Selection** | School (Gr 6-12) or College (UG/PG) — affects explanation tone & question types |
| **File Upload** | Upload PDF, TXT, DOCX textbooks/notes + syllabus |
| **Syllabus Mapping** | Parses units/modules/topics automatically; maps to material using TF-IDF |
| **Text Chunking** | Overlapping 800-word chunks with 100-word overlap for context retrieval |
| **Level-Adaptive Explanations** | Beginner / Intermediate / Advanced — Groq (llama3-70b) generates each |
| **Confidence Score** | TF-IDF similarity between topic and material → 0-100% score shown live |
| **Question Generation** | 2-mark, 5-mark, 10-mark (school) + 15-mark (college) exam questions |
| **Filterable Questions** | Filter by mark type in the UI |
| **Demo Mode** | Works without API key (sample content) |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

### 4. Get a free Groq API key
Visit [console.groq.com](https://console.groq.com) → Sign up → Create API Key  
Enter it in the app when prompted (starts with `gsk_`)

---

## 🔄 User Flow

```
Landing Page
    │
    ├── School Student ──────────────────────┐
    └── College Student ────────────────────┐│
                                            ││
                                    Upload Page (Step 2)
                                    ├── Upload textbook/notes (PDF/TXT)
                                    ├── Upload syllabus (optional)
                                    ├── Or paste syllabus text
                                    └── Enter Groq API key
                                            │
                                    Processing (Step 2→3)
                                    ├── Parse documents
                                    ├── Chunk text (800w, 100w overlap)
                                    ├── Parse syllabus → modules/topics
                                    └── Build TF-IDF index
                                            │
                                    Select Module & Topic (Step 3)
                                    ├── Visual module cards
                                    └── Topic chips per module
                                            │
                                    Learn Page (Step 4)
                                    ├── Level selector (Beginner/Intermediate/Advanced)
                                    ├── Explanation tab (Groq-generated)
                                    ├── Confidence score badge
                                    ├── Questions tab (2/5/10/15 mark)
                                    └── Sidebar topic navigator
```

---

## 🧠 Technical Architecture

### Syllabus Mapping (TF-IDF)
1. Text is chunked into 800-word overlapping windows
2. For each topic query, TF-IDF cosine similarity is computed against all chunks
3. Top-3 chunks are selected as context for the LLM
4. Confidence score = normalized similarity score (0-100)

### Groq Integration
- Model: `llama3-70b-8192`
- Explanations: structured prompt with context injection + level adaptation
- Questions: JSON-formatted output parsed client-side
- Temperature: 0.6 (balanced creativity/accuracy)

### Frontend Architecture
- Pure HTML/CSS/JS — no framework, no build step
- Multi-step wizard with animated transitions
- Drag-and-drop file upload
- Markdown renderer for explanation formatting
- Real-time skeleton loading states

---

## 📊 Confidence Score Logic

| Score | Meaning | Color |
|---|---|---|
| 70–100% | Topic well-covered in material | 🟢 Green |
| 40–69% | Topic partially covered | 🟡 Amber |
| 0–39% | Topic barely mentioned | 🔴 Red |

---

## 🎨 UI Design Notes

- **Typography**: Fraunces (editorial serif) + DM Sans (clean body)
- **Palette**: Warm paper tones, amber accent, sage/rust for status
- **Aesthetic**: Refined editorial — intentionally not generic AI
- **Animations**: Staggered fade-up on load, skeleton loaders, smooth transitions

---

## 🔧 API Endpoints

### `POST /api/parse-syllabus`
```json
{ "syllabus_text": "Unit 1: ..." }
→ { "modules": [{ "name": "...", "topics": ["..."] }] }
```

### `POST /api/explain`
```json
{
  "api_key": "gsk_...",
  "topic": "Newton's Laws",
  "module": "Mechanics",
  "material_text": "...",
  "level": "beginner",
  "student_type": "school"
}
→ { "explanation": "...", "confidence": 82, "chunks_used": 340 }
```

### `POST /api/questions`
```json
{
  "api_key": "gsk_...",
  "topic": "Newton's Laws",
  "module": "Mechanics",
  "student_type": "school",
  "level": "intermediate"
}
→ { "questions": [{ "mark": 2, "question": "...", "hint": "..." }] }
```

---

## 🛠 Extending the Project

- **PDF text extraction**: Use `PyPDF2` to extract text from uploaded PDFs in `app.py`
- **Vector DB**: Replace TF-IDF with ChromaDB + sentence-transformers for better retrieval
- **History**: Store sessions in SQLite using Flask-SQLAlchemy
- **Auth**: Add login with Flask-Login for personal study dashboards
- **Export**: Generate PDF question papers using ReportLab

---

## 📦 Dependencies

- `flask` — web server
- `flask-cors` — cross-origin requests
- `groq` — Groq API SDK (llama3-70b)
- `PyPDF2` — PDF text extraction
- `python-docx` — Word document parsing
