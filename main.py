from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pdfplumber
import requests
from io import BytesIO

app = FastAPI()

# Health check
@app.get("/ping")
async def ping():
    return {"status": "ok"}

# Upload a PDF file
@app.post("/extract_resume_text/")
async def extract_resume_text(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    try:
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return {"resume_text": text[:18000], "empty": len(text.strip()) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# JSON input for URL
class UrlRequest(BaseModel):
    url: str

@app.post("/extract_resume_text_from_url/")
async def extract_resume_text_from_url(request: UrlRequest):
    try:
        res
