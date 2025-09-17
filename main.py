from fastapi import FastAPI, UploadFile, File, HTTPException
import pdfplumber

app = FastAPI()

@app.post("/extract_resume_text/")
async def extract_resume_text(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported for MVP")
    try:
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        # clip to keep responses reasonable
        text = text[:18000]
        return {"resume_text": text, "empty": len(text.strip()) == 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
