from fastapi import FastAPI, UploadFile, File, HTTPException
import pdfplumber
import requests

app = FastAPI()

def extract_text_from_pdf(path: str) -> str:
    """Helper function to extract text from a PDF file path."""
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    # clip to keep responses reasonable
    return text[:18000]

@app.post("/extract_resume_text/")
async def extract_resume_text(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported for MVP")
    try:
        text = extract_text_from_pdf(file.file)
        return {"resume_text": text, "empty": len(text.strip()) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract_resume_text_from_url/")
async def extract_resume_text_from_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        text = extract_text_from_pdf("temp.pdf")
        return {"resume_text": text, "empty": len(text.strip()) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
