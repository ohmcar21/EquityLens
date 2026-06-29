"""Groq client wrapper using the official Groq Python SDK.

This module provides an async adapter to call the Llama 3.3 70B model
via Groq's API with the configured API key and generation parameters.
It returns the generated text only.
"""

from typing import Dict, Any

from groq import AsyncGroq

from app.config import get_settings


class GroqClientError(Exception):
    """Raised when the LLM call fails.

    NOTE: Temporarily keeping the name 'GroqClientError' so the rest
    of the codebase does not break. Will be renamed later.
    """
    pass


async def generate_text(
    prompt: str,
    temperature: float = None,
    max_output_tokens: int = None,
) -> Dict[str, Any]:
    """Call Groq (Llama 3.3 70B) with the given prompt and return text + meta.

    Args:
        prompt: The instruction prompt to send to the model.
        temperature: Model temperature (0-1). Defaults to config value.
        max_output_tokens: Max tokens in response. Defaults to config value.

    Returns:
        Dict with keys:
          - text: str (generated text)
          - model: str (model name used)
          - prompt_chars: int (length of input prompt)

    Raises:
        Groq ntError: If the API call fails or returns no content.
    """
    settings = get_settings()

    if not settings.groq_api_key:
        print("DEBUG [groq_client.py]: GROQ_API_KEY is not configured")
        raise GroqClientError("GROQ_API_KEY is not configured")

    api_key = settings.groq_api_key.strip()
    temperature = temperature if temperature is not None else settings.llm_temperature
    max_output_tokens = max_output_tokens if max_output_tokens is not None else settings.llm_max_output_tokens

    model_name = "llama-3.3-70b-versatile"

    client = AsyncGroq(api_key=api_key)

    try:
        chat_completion = await client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=temperature,
            max_tokens=max_output_tokens,
        )
    except Exception as e:
        print(f"DEBUG [groq_client.py]: Exception during Groq API call: {type(e).__name__} - {e}")
        raise GroqClientError(f"Groq API error: {e}")

    # Validate response has content
    if not chat_completion or not chat_completion.choices:
        print(f"DEBUG [groq_client.py]: Empty response or no choices. Response: {chat_completion}")
        raise GroqClientError("Groq returned empty response")

    text = chat_completion.choices[0].message.content

    if not text:
        print("DEBUG [groq_client.py]: Response choice has no content.")
        raise GroqClientError("Groq returned empty content")

    return {
        "text": text,
        "model": model_name,
        "prompt_chars": len(prompt),
    }
