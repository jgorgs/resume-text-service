from fastapi import FastAPI, HTTPException
import pdfplumber
import requests
import tempfile
import os

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/extract_resume_text_from_url/")
async def extract_resume_text_from_url(payload: dict):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")

    try:
        # Download PDF
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        # Extract text
        text = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        os.remove(tmp_path)

        return {
            "resume_text": text[:18000],  # Clip to 18k chars max
            "empty": len(text.strip()) == 0,
            "source_url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
