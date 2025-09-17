from fastapi import FastAPI, HTTPException
import pdfplumber
import requests
import tempfile
import os
from requests.exceptions import RequestException

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
        # Fetch PDF with timeout and check response
        response = requests.get(url, timeout=15, stream=True)
        response.raise_for_status()
        
        # Verify content-type is PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type:
            return {
                "resume_text": "",
                "empty": True,
                "source_url": url,
                "error": "URL did not return a PDF (e.g., HTML or redirect)"
            }
        
        # Save temporarily and extract text
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            tmp_path = tmp.name
        
        text = ""
        try:
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text
                    if len(text) > 18000:  # Clip early to avoid memory overload
                        break
        finally:
            os.remove(tmp_path)
        
        text = text.strip()
        return {
            "resume_text": text[:18000],  # Final clip for consistency
            "empty": len(text) == 0,
            "source_url": url
        }
    
    except RequestException as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except pdfplumber.PDFSyntaxError as e:
        raise HTTPException(status_code=500, detail=f"PDF parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
