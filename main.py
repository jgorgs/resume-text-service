from fastapi import FastAPI, UploadFile, File, HTTPException
import pdfplumber
import requests
import io

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "ok"}

# Extract from uploaded file
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

# Extract from a URL
@app.post("/extract_resume_text_from_url/")
async def extract_resume_text_from_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_bytes = io.BytesIO(response.content)

        text = ""
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        return {"resume_text": text[:18000], "empty": len(text.strip()) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
