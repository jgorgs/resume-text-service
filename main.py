from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pdfplumber
import requests
import os

app = FastAPI()

# -------------------------
# Helper: extract text from PDF file
# -------------------------
def extract_text(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


# -------------------------
# Endpoint 1: Upload a file directly
# -------------------------
@app.post("/extract_resume_text/")
async def extract_resume_text(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported for MVP")
    try:
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        # Clip to keep responses reasonable
        text = text[:18000]
        return {"resume_text": text, "empty": len(text.strip()) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Endpoint 2: Pass a URL (now expects JSON body)
# -------------------------
class UrlRequest(BaseModel):
    url: str

@app.post("/extract_resume_text_from_url/")
async def extract_resume_text_from_url(request: UrlRequest):
    try:
        response = requests.get(request.url)
        response.raise_for_status()

        temp_path = "temp_resume.pdf"
        with open(temp_path, "wb") as f:
            f.write(response.content)

        text = extract_text(temp_path)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {"resume_text": text[:18000], "empty": len(text.strip()) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
