"""
FastAPI backend for the SME AI Advisor dashboard.
Exposes two endpoints:
  POST /api/recommend  — calls Claude, returns JSON result
  POST /api/pdf        — takes JSON result, returns PDF bytes
"""

import json, os, tempfile, base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from anthropic import Anthropic

from prompts import build_system_prompt, build_user_prompt
from pdf_generator import generate_pdf
from pricing import collect_all_pricing, format_pricing_for_prompt

ANTHROPIC_API_KEY = os.environ.get(
    "ANTHROPIC_API_KEY",
    ""
)

app = FastAPI(title="SME AI Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    industry: str
    common_answers: dict
    industry_answers: dict
    extra_context: str = ""


class PdfRequest(BaseModel):
    result: dict
    industry: str


@app.post("/api/recommend")
async def recommend(req: RecommendRequest):
    try:
        pricing_text = ""
        try:
            pricing_data = collect_all_pricing(gcp_api_key=None, vastai_key=None, runpod_key=None)
            pricing_text = format_pricing_for_prompt(pricing_data)
        except Exception:
            pricing_data = None

        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        system = build_system_prompt()
        user_msg = build_user_prompt(
            req.industry, req.common_answers,
            req.industry_answers, req.extra_context, pricing_text
        )
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=0,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        result = json.loads(raw)
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/pdf")
async def make_pdf(req: PdfRequest):
    try:
        tmp = os.path.join(tempfile.gettempdir(), f"sme_{os.getpid()}.pdf")
        generate_pdf(req.result, req.industry, tmp)
        with open(tmp, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode()
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return JSONResponse({"ok": True, "pdf_b64": pdf_b64})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
