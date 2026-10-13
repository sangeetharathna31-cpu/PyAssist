"""Gemini AI Service integration for PyAssist.
Provides real-time Python reasoning, code generation, debugging,
algorithm explanation, and code review using the Google Gemini API.
"""
import os
import re
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple, List
from google import genai
from google.genai.errors import APIError

from pyassist.app.config import settings

logger = logging.getLogger("pyassist.gemini")

MODE_PROMPTS = {
    "ask": (
        "You are PyAssist, an expert Python programming assistant and mentor. "
        "Answer the user's Python question with clear explanations, practical tips, "
        "and idiomatic Python 3 examples. If code is helpful, include readable, tested Python snippets."
    ),
    "generate": (
        "You are PyAssist Code Generator. "
        "Generate clean, robust, and idiomatic Python 3 code for the user's requirements. "
        "Structure your response with:\n"
        "1. Brief summary of the approach\n"
        "2. Complete Python implementation with comments\n"
        "3. Usage example and expected console output"
    ),
    "debug": (
        "You are PyAssist Python Debugger. "
        "Diagnose the user's Python bug, exception, or stack traceback. "
        "Structure your response with:\n"
        "1. Root Cause Analysis: Exactly what caused the error (e.g. IndexError, TypeError, logic flaw)\n"
        "2. Corrected Python Code: The fixed snippet\n"
        "3. Prevention Tips: Best practices to avoid this bug in the future"
    ),
    "explain": (
        "You are PyAssist Code Explainer. "
        "Analyze the provided Python code in detail. "
        "Structure your response with:\n"
        "1. High-level Purpose & Behavior\n"
        "2. Step-by-Step Breakdown of key lines or constructs\n"
        "3. Algorithmic Complexity (Time & Space Complexity) where applicable"
    ),
    "review": (
        "You are PyAssist Senior Code Reviewer. "
        "Perform a thorough, constructive code review of the user's Python code. "
        "Structure your response with:\n"
        "1. Code Quality & PEP 8 Compliance\n"
        "2. Performance & Efficiency Considerations\n"
        "3. Edge Cases & Potential Bugs\n"
        "4. Refactored / Recommended Version"
    ),
}

def extract_primary_code_block(markdown_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract first major python code block and optional expected output from markdown."""
    code_match = re.search(r"```(?:python|py)?\n(.*?)```", markdown_text, re.DOTALL)
    code_snippet = code_match.group(1).strip() if code_match else None

    output_match = re.search(r"```(?:output|text|console)?\n(.*?)```", markdown_text, re.DOTALL)
    output_snippet = None
    if output_match and output_match.group(0) != (code_match.group(0) if code_match else ""):
        output_snippet = output_match.group(1).strip()

    return code_snippet, output_snippet

def _call_gemini_sync(prompt: str, mode: str, model_name: str) -> Tuple[str, str]:
    """Synchronous execution of Gemini API generate_content with backoff retry."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in server environment.")

    client = genai.Client(api_key=api_key)
    system_instruction = MODE_PROMPTS.get(mode, MODE_PROMPTS["ask"])

    config = {
        "system_instruction": system_instruction,
        "temperature": 0.4 if mode in ("debug", "review") else 0.7,
    }

    import time
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            if not response.text:
                raise ValueError("Empty response received from Gemini model.")
            return response.text, model_name
        except Exception as exc:
            err_str = str(exc)
            if ("503" in err_str or "UNAVAILABLE" in err_str) and attempt < max_retries - 1:
                logger.info(f"Retrying model {model_name} after 503 spike (attempt {attempt+1})...")
                time.sleep(1.2)
                continue
            logger.warning(f"Gemini call failed with model '{model_name}': {exc}")
            raise exc

async def generate_gemini_response(
    question: str,
    mode: str = "ask",
    preferred_model: Optional[str] = None
) -> Dict[str, Any]:
    """Execute Gemini request with timeout, validation, and multi-model fallback."""
    if not settings.GEMINI_API_KEY:
        return {
            "success": False,
            "error_type": "missing_api_key",
            "message": "Gemini API key is not configured. Falling back to deterministic knowledge base."
        }

    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    if settings.GEMINI_PRIMARY_MODEL not in models_to_try:
        models_to_try.append(settings.GEMINI_PRIMARY_MODEL)
    for fb in settings.GEMINI_FALLBACK_MODELS:
        if fb not in models_to_try:
            models_to_try.append(fb)

    last_error = None
    for model_name in models_to_try:
        try:
            loop = asyncio.get_event_loop()
            text, used_model = await asyncio.wait_for(
                loop.run_in_executor(None, _call_gemini_sync, question, mode, model_name),
                timeout=settings.GEMINI_TIMEOUT_SECONDS
            )

            code_snippet, expected_output = extract_primary_code_block(text)

            return {
                "success": True,
                "content": text,
                "code_example": code_snippet,
                "expected_output": expected_output,
                "model_used": used_model,
                "mode": mode,
            }

        except asyncio.TimeoutError:
            logger.error(f"Timeout calling Gemini with model {model_name} after {settings.GEMINI_TIMEOUT_SECONDS}s")
            last_error = f"Request timed out with model {model_name}."
            continue
        except APIError as api_err:
            logger.error(f"Gemini API Error with {model_name}: {api_err}")
            last_error = str(api_err)
            # Try next model if 503 unavailable
            if "503" in str(api_err) or "UNAVAILABLE" in str(api_err):
                continue
            # Quota exceeded or permission
            if "429" in str(api_err) or "RESOURCE_EXHAUSTED" in str(api_err):
                return {
                    "success": False,
                    "error_type": "quota_exceeded",
                    "message": "Gemini API rate limit or quota exceeded. Please wait a moment before trying again."
                }
            continue
        except Exception as exc:
            logger.error(f"Unexpected error calling Gemini with {model_name}: {exc}")
            last_error = str(exc)
            continue

    return {
        "success": False,
        "error_type": "all_models_failed",
        "message": f"Unable to reach Gemini models. Detail: {last_error}"
    }
