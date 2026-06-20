"""Prompt templates for AI Insights (EquityLens).

This module builds a conservative, production-ready prompt that:
- Requires the model to ONLY interpret the provided analytics JSON.
- Prohibits calculations, inventing values, and buy/sell recommendations.
- Enforces a concise (200-300 word) dashboard-friendly report structure with
  explicit sections:
    1. Executive Summary
    2. Portfolio Health
    3. Diversification Analysis
    4. Sector Exposure Analysis
    5. Strengths
    6. Risks & Monitoring Areas
    7. Portfolio Intelligence Summary
- Requires a leading "Facts" block listing the exact numeric inputs used.

Usage:
    from app.ai.prompt_templates import build_prompt
    prompt = build_prompt(payload_dict)
    # send `prompt` to the LLM
"""

from typing import Any, Dict
import json


SYSTEM_INSTRUCTIONS = (
    "You are an assistant whose ONLY responsibility is to INTERPRET the analytics JSON "
    "provided in the payload. Do NOT perform any calculations, transformations, or "
    "inferences beyond restating and interpreting the supplied numbers. Do NOT invent "
    "or hallucinate facts. Do NOT provide buy or sell recommendations or any form of "
    "financial advice. Keep all output professional and suitable for display in a "
    "single dashboard card."
)


USER_INSTRUCTIONS_PREFIX = (
    "Task: Using only the JSON payload supplied below, produce a concise, investor-friendly "
    "report between 200 and 300 words suitable for a dashboard card. Follow these rules exactly:\n\n"
    "Rules:\n"
    "1) Use ONLY the fields present in the payload. If a required field is missing or null, "
    "write 'insufficient data' for that item—do not infer or compute it.\n"
    "2) Begin with a short 'Facts' block that echoes the exact numeric inputs used (numbers must "
    "match the payload values verbatim).\n"
    "3) After the Facts block, provide the report text with the following ordered sections:\n"
    "   - Executive Summary (1 sentence)\n"
    "   - Portfolio Health (one short paragraph referencing overall_score, grade, status, and subscores)\n"
    "   - Diversification Analysis (interpret diversification.breakdown fields)\n"
    "   - Sector Exposure Analysis (interpret top sector_summary entries and their percentages)\n"
    "   - Strengths (2 short bullets)\n"
    "   - Risks & Monitoring Areas (2 short bullets; non-actionable)\n"
    "   - Portfolio Intelligence Summary (1 short sentence restating the overall quality)\n"
    "4) Do NOT include buy/sell guidance, portfolio rebalancing instructions, or actionable trading steps.\n"
    "5) Keep the entire narrative (excluding the Facts block) between 200 and 300 words. Aim for clarity.\n"
    "6) Output only the report (Facts block + report). Do not include any extra analysis, code, or metadata.\n"
)


OUTPUT_TEMPLATE = (
    "=== Facts ===\n"
    "<List the exact numeric fields used, e.g. 'Health: overall_score=87.96; diversification=79.13; ...'>\n\n"
    "=== Report ===\n"
    "Executive Summary:\n"
    "<one sentence>\n\n"
    "Portfolio Health:\n"
    "<one short paragraph>\n\n"
    "Diversification Analysis:\n"
    "<short paragraph>\n\n"
    "Sector Exposure Analysis:\n"
    "<short paragraph>\n\n"
    "Strengths:\n"
    "- <bullet>\n"
    "- <bullet>\n\n"
    "Risks & Monitoring Areas:\n"
    "- <bullet>\n"
    "- <bullet>\n\n"
    "Portfolio Intelligence Summary:\n"
    "<one short sentence>\n"
)


def _serialize_payload(payload: Dict[str, Any]) -> str:
    """Serialize the compact payload to JSON for injection into the prompt.

    Uses compact separators to keep prompt length small while preserving keys and values.
    """
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def build_prompt(payload: Dict[str, Any]) -> str:
    """Build the full instruction prompt string for the LLM.

    Expected payload keys (compact analytics snapshot):
      - health
      - diversification
      - sector_summary
      - top_holdings
      - recommendations

    Returns a single string suitable to pass to the LLM's text-generation call.
    """
    payload_json = _serialize_payload(payload)

    instruction = (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"{USER_INSTRUCTIONS_PREFIX}\n\n"
        f"PAYLOAD:\n{payload_json}\n\n"
        f"OUTPUT_FORMAT_GUIDANCE:\n{OUTPUT_TEMPLATE}\n\n"
        "Remember: DO NOT calculate or invent values. Echo numbers exactly as provided.\n"
    )
    return instruction
