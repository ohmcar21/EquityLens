"""Gemini client wrapper using google-generativeai SDK 0.8.6.

This module provides a thin async adapter to call the Gemini 1.5 Flash model
with the configured API key and generation parameters. It returns generated
text and metadata without any analytics logic or database operations.
"""

from typing import Dict, Any

import google.generativeai as genai

from app.config import get_settings

settings = get_settings()


class GeminiClientError(Exception):
    """Raised when Gemini call fails."""
    pass


async def generate_text(
    prompt: str,
    temperature: float = None,
    max_output_tokens: int = None,
) -> Dict[str, Any]:
    """Call Gemini 2.5 Flash with the given prompt and return text + meta.

    Args:
        prompt: The instruction prompt to send to Gemini.
        temperature: Model temperature (0-1). Defaults to config value.
        max_output_tokens: Max tokens in response. Defaults to config value.

    Returns:
        Dict with keys:
          - text: str (generated text)
          - model: str (model name used)
          - prompt_chars: int (length of input prompt)

    Raises:
        GeminiClientError: If the API call fails or returns no content.
    """
    if not settings.gemini_api_key:
        raise GeminiClientError("GEMINI_API_KEY is not configured")

    api_key = settings.gemini_api_key.strip()

    temperature = temperature if temperature is not None else settings.llm_temperature
    max_output_tokens = max_output_tokens if max_output_tokens is not None else settings.llm_max_output_tokens

    # Configure the Gemini SDK with the API key
    genai.configure(api_key=api_key)

    # Create model instance
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    try:
        # Use async generate_content_async method
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        )
    except Exception as e:
        raise GeminiClientError(f"Gemini API error: {e}")

    # Validate response has content
    if not response or not response.text:
        raise GeminiClientError("Gemini returned empty response")

    return {
        "text": response.text,
        "model": "models/gemini-2.5-flash",
        "prompt_chars": len(prompt),
    }