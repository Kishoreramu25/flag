import os
import shutil
import tempfile
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from detector import AIContentDetector
from parser import DocumentParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPIServer")

# Global instances loaded on startup
detector = None
parser = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the GPT-2 model and nltk packages
    global detector, parser
    logger.info("Initializing models on startup...")
    try:
        detector = AIContentDetector()
        parser = DocumentParser()
        logger.info("Startup initialization complete.")
    except Exception as e:
        logger.error(f"Startup initialization failed: {e}")
        # We don't crash, but log the error
    yield
    # Shutdown: Clean up if needed
    logger.info("Server shutting down.")

app = FastAPI(
    title="AI Content Detector API",
    description="FastAPI backend to detect AI generated content in documents.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File configuration
MAX_FILE_SIZE_MB = 10
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.html', '.css', '.js', '.json'}

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint with model status"""
    status_info = {
        "status": "healthy" if detector else "unhealthy",
        "model_loaded": detector is not None,
        "device": detector.device if detector else "unknown",
        "models": {
            "gpt2_loaded": detector is not None,
            "roberta_detector": detector.roberta_available if detector else False,
            "sentiment_analyzer": detector.sentiment_available if detector else False
        }
    }
    return status_info

@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """
    Accepts PDF, DOCX, TXT file uploads (max 10MB)
    Extracts text and runs AI content detection algorithms
    """
    if detector is None or parser is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Detection models are not initialized yet."
        )

    # 1. Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {ext}. Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # 2. Validate file size (10MB limit)
    # Read chunk by chunk to check size without overflowing memory
    size = 0
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"upload_{file.filename}")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # read 1MB chunks
                size += len(chunk)
                if size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File size exceeds the {MAX_FILE_SIZE_MB}MB limit."
                    )
                buffer.write(chunk)
    except HTTPException:
        # Re-raise size HTTP exceptions
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        logger.error(f"Error saving uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file."
        )

    # 3. Process & Parse Document (within a 30-second timeout)
    try:
        # Running parsing in a separate thread/task to prevent blocking the event loop
        # and enforce a 30-second timeout limit.
        async def parse_and_detect():
            parsed_data = parser.parse_file(temp_file_path)
            if not parsed_data["text"].strip():
                raise ValueError("The uploaded document is empty.")
            
            # Run AI Content Detector
            result = detector.analyze_document(parsed_data["paragraphs"])
            return result

        # Wait with 30s timeout
        result_data = await asyncio.wait_for(parse_and_detect(), timeout=30.0)
        return result_data

    except asyncio.TimeoutError:
        logger.error("Processing timed out after 30 seconds.")
        raise HTTPException(
            status_code=status.HTTP_504_TIMEOUT,
            detail="Processing timed out. The document is too large or server is overloaded."
        )
    except ValueError as val_err:
        logger.warning(f"Validation error: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal analysis failure: {str(e)}"
        )
    finally:
        # Cleanup temporary uploaded file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as cleanup_err:
                logger.warning(f"Failed to clean up temp file {temp_file_path}: {cleanup_err}")

if __name__ == "__main__":
    import uvicorn
    # Local boot on port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
