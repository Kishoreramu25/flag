# AI Content Detector Backend

This is the Python FastAPI backend for the AI Content Detector. It parses documents (PDF, DOCX, TXT) and evaluates the probability of content being AI-generated using three key statistical metrics: Perplexity, Burstiness, and Shannon entropy.

## Features
- **Lifespan Loader**: Loads HuggingFace `gpt2` model into memory once on server startup to ensure fast responses.
- **Multimodal Parser**: Text extraction from PDFs (`PyMuPDF`), DOCX (`python-docx`), and plain text.
- **Robust Scoring**: Calculates perplexity scores (predictability), sentence burstiness (length variance), and word token entropy.
- **CORS Configured**: Ready to interface with frontend clients running on `http://localhost:3000` or `http://localhost:5173`.
- **System Boundaries**: 10MB upload limit, 30s timeout checks, CPU-fallback execution.

## Installation

### Prerequisites
- Python 3.9 - 3.11
- pip package manager

### 1. Setup Virtual Environment
Run the following commands from this `backend` directory:
```bash
python -m venv venv
# On Windows PowerShell:
venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

> [!NOTE]
> On systems without CUDA-compatible GPUs, PyTorch will install the CPU version by default. The detector will automatically fall back to CPU execution.

## Running the Server

Start the FastAPI application with Uvicorn:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The server will start at: **`http://127.0.0.1:8000`**

- **Health Check**: `GET http://127.0.0.1:8000/health`
- **Interactive Documentation (Swagger)**: `http://127.0.0.1:8000/docs`

## API Reference

### `POST /api/analyze`
Accepts a document file and returns paragraph-by-paragraph and overall AI detection metrics.

- **Content-Type**: `multipart/form-data`
- **Body**: `file` (PDF, DOCX, or TXT file, max 10MB)

#### Example Response
```json
{
  "overall_ai_percentage": 72,
  "confidence": 88,
  "word_count": 324,
  "ai_words": 233,
  "paragraphs": [
    {
      "text": "Large language models have completely revolutionized...",
      "ai_score": 85,
      "confidence": 91,
      "perplexity_score": 0.85,
      "burstiness_score": 0.72,
      "entropy_score": 0.88,
      "flag": "Very High"
    }
  ]
}
```
