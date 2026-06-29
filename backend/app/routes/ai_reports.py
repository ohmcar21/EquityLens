"""Debug routes for AI payload and prompt generation.

This module provides a single POST endpoint used for verifying the compact
payload produced for the LLM and the prompt built from it. It does not call
any external LLM, persist data, or schedule background work.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.ai_service import build_payload_and_prompt, generate_report
from app.ai.groq_client import GroqClientError

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


@router.post("/debug")
async def debug_ai_payload(db: AsyncSession = Depends(get_db)):
    """Return the compact LLM payload and the generated prompt for debugging.

    Response shape:
      { "payload": {...}, "prompt": "..." }
    """
    try:
        result = await build_payload_and_prompt(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/report")
async def create_ai_report(db: AsyncSession = Depends(get_db)):
    """
    Generate an AI portfolio report using Groq.
    """
    try:
        result = await generate_report(db)
        return result

    except GroqClientError as e:
        print(f"DEBUG [ai_reports.py]: Caught GroqClientError: {repr(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"AI service unavailable: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
