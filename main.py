from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from analyzer import analyze_policy_compliance, generate_fixed_policy
import asyncio

app = FastAPI(title="DSCI/DPDP Compliance Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PolicyResponse(BaseModel):
    gaps: list
    compliance_score: int

@app.post("/analyze", response_model=PolicyResponse)
async def analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        # Basic text extraction (expand with PyPDF2 if needed)
        user_text = content.decode('utf-8', errors='ignore')
        
        if len(user_text) < 50:
            raise HTTPException(status_code=400, detail="File too small or empty.")
        
        # Run analysis
        gaps = analyze_policy_compliance(user_text)
        
        # Calculate a mock score based on gaps
        severity_map = {"High": 10, "Medium": 5, "Low": 2}
        total_penalty = sum(severity_map.get(g.get("severity", "Low"), 2) for g in gaps)
        score = max(0, 100 - total_penalty)
        
        return PolicyResponse(gaps=gaps, compliance_score=score)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fix")
async def fix_policy(file: UploadFile = File(...), gaps: str = "[]"):
    try:
        content = await file.read()
        user_text = content.decode('utf-8', errors='ignore')
        gaps_list = json.loads(gaps)
        
        fixed_text = generate_fixed_policy(user_text, gaps_list)
        return {"status": "success", "revised_policy": fixed_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
