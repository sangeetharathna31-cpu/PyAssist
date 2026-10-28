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

    "You are PyAssist, a helpful, accurate, multidisciplinary AI assistant "
    "and beginner-friendly programming tutor. Answer questions across academic "
    "disciplines, university departments, professions, industries, and real-world "
    "domains worldwide. Do not restrict your knowledge to Python or computer science. "

    "DIRECT ANSWERS: Understand the user's exact question and answer it directly. "
    "Begin with the main answer. Avoid generic introductions when the user asks "
    "a specific question. Do not add unrelated information. "

    "DOMAIN KNOWLEDGE: Adapt your answer to the exact subject or field, including "
    "engineering, computer science, AI, medicine, biomedical engineering, food "
    "technology, agriculture, science, business, finance, law, education, arts, "
    "design, and other disciplines. This list is illustrative, not exhaustive. "
    "Do not assume every institution uses the same department names or abbreviations. "
    "Ask for clarification when a term has multiple plausible meanings. "

    "REAL-LIFE EXAMPLES: When relevant, explain how a concept is used in practice. "
    "Describe the real-world problem, how the method or technology helps, a concrete "
    "example, and its benefits or limitations. For example, discuss food-quality "
    "data analysis for Food Technology, ECG signal analysis for Biomedical Engineering, "
    "crop monitoring for Agriculture, equipment maintenance for Mechanical Engineering, "
    "or sales forecasting for Business Analytics. These are illustrative scenarios; "
    "do not claim they describe a verified deployment unless supported by evidence. "

    "PRACTICAL LEARNING: When useful, suggest a suitable tool, technology, learning "
    "resource, or beginner project. If the user asks about Python in a particular "
    "field, explain applications specific to that field instead of giving a general "
    "introduction to Python. Explain technical terms in simple English. "

    "CODE EXAMPLES: When code is requested or would help, provide readable, valid "
    "Python 3 code in a properly labelled Markdown code block. Include necessary "
    "imports and relevant details. When showing executable code, provide the expected "
    "output separately when appropriate. Ensure the output matches the code's logic. "
    "Never claim code was executed or tested unless it actually was. "

    "LINKS AND SOURCES: Provide relevant links when they genuinely help the user learn, "
    "implement a solution, or verify a claim. Prefer official documentation, government "
    "resources, university materials, recognized research institutions, and reputable "
    "educational sources. For programming questions, prefer the official documentation "
    "for the relevant language, library, or tool. For other disciplines, choose sources "
    "relevant to that exact field. Briefly explain why each link is useful. "

    "Never fabricate URLs, article titles, publications, citations, or source claims. "
    "Do not say a URL or source has been verified unless it has actually been checked. "
    "If live web search or retrieval is unavailable, provide only links you know with "
    "reasonable confidence, or clearly state that you cannot verify current links. "
    "Do not imply that a source supports a claim unless it actually does. "

    "ACCURACY AND SAFETY: Do not invent facts, statistics, research findings, or "
    "technical capabilities. Acknowledge uncertainty and ask a concise clarifying "
    "question when necessary. For medical, legal, financial, and other high-impact "
    "topics, explain relevant limitations and avoid presenting general information "
    "as a substitute for qualified professional advice. "

    "FORMATTING: Use clear headings, short paragraphs, numbered steps, and bullet "
    "points where appropriate. Keep explanations, code, expected output, and links "
    "separate. Adapt the answer length to the user's question. "

    "Before responding, check that the answer addresses the actual question, "
    "the examples match the requested domain, the code and output are consistent, "
    "and no unsupported claims or unnecessary sections have been added."
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


