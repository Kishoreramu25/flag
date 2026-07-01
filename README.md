# AI Content Detector 🔍

A full-stack application to detect AI-generated content in documents (PDFs, DOCX, TXT). Detects content from all LLMs (Claude, GPT, Llama, Gemini, etc.) using advanced statistical analysis.

## 📋 Project Structure

```
flag/
├── frontend/                 (React/Vite + Tailwind CSS)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx   (Home page)
│   │   │   ├── Upload.jsx    (File upload)
│   │   │   └── Results.jsx   (Analysis results)
│   │   ├── App.jsx           (Main router)
│   │   ├── App.css           (Styles)
│   │   ├── main.jsx          (Entry point)
│   │   └── index.css         (Tailwind imports)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.local
│
├── backend/                  (FastAPI + Python)
│   ├── main.py              (FastAPI server)
│   ├── detector.py          (AI detection engine)
│   ├── parser.py            (Document parser)
│   ├── requirements.txt
│   └── test_backend.py
│
└── README.md
```

---

## 🚀 Quick Start

### Frontend Setup (5 minutes)

```bash
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:5173`

**Required packages:**
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios
- Lucide Icons

### Backend Setup (5 minutes)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server runs on: `http://localhost:8000`

**API endpoint:**
```
POST /api/analyze
Content-Type: multipart/form-data

Request: file (PDF/DOCX/TXT)
Response: JSON with AI detection results
```

---

## 🔧 Backend Architecture

### Detection Engine (`detector.py`)

Uses **statistical analysis** to detect AI content from ANY LLM:

1. **Perplexity**: Measures text predictability
   - AI text: LOWER perplexity
   - Human text: HIGHER perplexity
   
2. **Burstiness**: Sentence length variation
   - AI text: UNIFORM (low burstiness)
   - Human text: VARIED (high burstiness)

3. **Entropy**: Vocabulary diversity
   - AI text: LOWER entropy
   - Human text: HIGHER entropy

### Result Format

```json
{
  "analysis_id": "uuid",
  "overall_ai_percentage": 68.5,
  "confidence_score": 92.3,
  "total_words": 3247,
  "ai_words": 2207,
  "processing_time": 4.52,
  "paragraph_results": [
    {
      "text": "Paragraph content...",
      "ai_score": 85.2,
      "metrics": {
        "perplexity": 45.23,
        "burstiness": 0.82,
        "entropy": 4.51
      }
    }
  ]
}
```

---

## 🎨 Frontend Features

### Landing Page
- Hero section with CTA
- Feature highlights (All LLMs, Detailed Breakdown, Private & Secure)
- How it works explanation

### Upload Page
- Drag & drop file upload
- File validation (type & size)
- Error handling & feedback

### Results Page
- Overall AI% score with circular progress
- Confidence level indicator
- Word statistics
- **Expandable paragraph breakdown**
- Color-coded badges (Very High/High/Medium/Low)
- Download report (JSON export)
- Analyze another document button

---

## 🔌 API Endpoints

### Health Check
```
GET /health
Response: { "status": "healthy", "model_loaded": true, "device": "cpu/cuda" }
```

### Analyze Document
```
POST /api/analyze
Content-Type: multipart/form-data

Request:
  - file: File (PDF, DOCX, TXT, max 10MB)

Response: 200 OK
  {JSON with detection results}

Error Responses:
  - 400: Invalid file format/size
  - 503: Model not initialized
  - 504: Processing timeout (>30s)
  - 500: Internal server error
```

---

## 🛠️ Configuration

### Frontend Environment (.env.local)
```
VITE_BACKEND_URL=http://localhost:8000
```

### Backend Configuration
- Max file size: 10MB
- Supported formats: PDF, DOCX, TXT, MD, HTML, CSS, JS, JSON
- Processing timeout: 30 seconds
- CORS origins: localhost:3000, localhost:5173

---

## 📊 Accuracy

- **Overall Accuracy**: ~80-85% across all LLMs
- **Model-agnostic**: Works on Claude, GPT, Llama, Gemini, etc.
- **Per-paragraph analysis**: Detailed breakdown of suspicious sections
- **Confidence scores**: Indicates reliability of detection

---

## 🚢 Deployment

### Frontend (Vercel)
```bash
npm run build
vercel deploy
```

Set environment variable:
- `VITE_BACKEND_URL` = Your backend URL

### Backend (Heroku/Railway/Fly.io)
```bash
git push heroku main
# OR
railway deploy
```

---

## 🔐 Security

- File uploads are validated (type & size)
- Temporary files are cleaned up immediately
- No files are permanently stored
- CORS configured for frontend only
- XSS protection (React auto-escapes)

---

## 📦 Dependencies

### Frontend
- `react` - UI library
- `react-router-dom` - Routing
- `axios` - HTTP client
- `tailwindcss` - Styling
- `lucide-react` - Icons
- `vite` - Build tool

### Backend
- `fastapi` - Web framework
- `python-multipart` - File uploads
- `transformers` - GPT-2 model
- `torch` - Deep learning
- `pymupdf` - PDF parsing
- `python-docx` - DOCX parsing
- `nltk` - Text processing
- `textstat` - Readability metrics
- `numpy` - Numerical computing

---

## 🧪 Testing

### Frontend
```bash
cd frontend
npm run dev
# Visit http://localhost:5173
```

### Backend
```bash
cd backend
python test_backend.py
```

---

## 📝 Development Notes

- Frontend uses React Router for SPA navigation
- Backend uses FastAPI async for scalability
- Detection uses statistical methods (no API calls)
- All analysis is done locally (private by default)
- Response time typically 2-10 seconds depending on document size

---

## 🎯 Next Steps

1. **Set up environment** (follow Quick Start)
2. **Test locally** (npm run dev + python main.py)
3. **Deploy frontend** (Vercel)
4. **Deploy backend** (Heroku/Railway)
5. **Connect APIs** (update VITE_BACKEND_URL in Vercel)

---

## 📚 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Routing | React Router v6 |
| HTTP | Axios |
| Backend | FastAPI + Uvicorn |
| AI Detection | GPT-2 + Statistical Analysis |
| Document Parsing | PyMuPDF + python-docx |
| Database | Optional (Supabase for history) |

---

## 📄 License

MIT License - Feel free to use and modify

---

**Built with ❤️ for detecting AI content across all LLMs**
