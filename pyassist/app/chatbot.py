"""Chatbot retrieval engine for PyAssist.
Uses normalized text processing, transparent multi-factor scoring,
and confidence thresholds to answer Python questions deterministically.
"""
import re
from typing import Dict, Any, List, Tuple
from pyassist.app.knowledge_base import TOPICS

# Common conversational stop words to ignore during word-level scoring
STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with",
    "is", "are", "was", "were", "be", "been", "being",
    "what", "how", "why", "when", "where", "who", "which",
    "can", "could", "would", "should", "do", "does", "did",
    "please", "tell", "me", "about", "explain", "give", "example",
    "difference", "between", "versus", "vs", "and", "or", "i", "you"
}

def normalize_text(text: str) -> str:
    """Normalize input text: lowercased, spaces trimmed, punctuation normalized."""
    text = text.lower().strip()
    # Protect compound operators before normalizing single equals
    text = text.replace("==", " __DBL_EQ__ ").replace("!=", " __NOT_EQ__ ")
    text = text.replace("=", " = ")
    text = text.replace("__DBL_EQ__", " == ").replace("__NOT_EQ__", " != ")
    # Keep alphanumeric, spaces, and operators == and =
    text = re.sub(r"[^\w\s=\+\-\*/<>]", " ", text)
    # Collapse multiple whitespaces
    return " ".join(text.split())

def extract_tokens(normalized_text: str) -> List[str]:
    """Tokenize and filter stop words, keeping operators and keywords."""
    tokens = normalized_text.split()
    return [t for t in tokens if len(t) > 1 or t in ("=", "==")]

def stem_word(w: str) -> str:
    """Simple rule-based suffix normalization for English/Python words."""
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    if w.endswith("ing") and len(w) > 5:
        return w[:-3]
    if w.endswith("ed") and len(w) > 4:
        return w[:-2]
    return w

def score_topic(normalized_query: str, query_tokens: List[str], topic_data: Dict[str, Any]) -> float:
    """
    Transparent relevance scoring algorithm:
    1. Exact keyword phrase match: +80 to +120 points
    2. Substring keyword match: +30 to +50 points
    3. Token overlap with topic title & keywords: +8 to +15 points per matched token
    4. Special operator checks (e.g., '==' vs '=')
    """
    score = 0.0
    stemmed_query_tokens = [stem_word(t) for t in query_tokens]

    keywords = topic_data.get("keywords", [])
    title_lower = topic_data.get("title", "").lower()

    # 1. Exact phrase check against keywords with word boundary matching
    padded_query = f" {normalized_query} "
    for kw in keywords:
        kw_norm = normalize_text(kw)
        if not kw_norm:
            continue
        if kw_norm == normalized_query:
            score += 100.0
            break
        elif f" {kw_norm} " in padded_query:
            score += 45.0
        elif len(kw_norm) >= 6 and re.search(r"\b" + re.escape(kw_norm) + r"\b", normalized_query):
            score += 35.0

    # 2. Operator specific matching
    if topic_data["id"] == "equals_vs_assign":
        if "==" in normalized_query and "=" in normalized_query:
            score += 90.0
        elif "==" in normalized_query:
            score += 40.0
    elif topic_data["id"] == "is_vs_equals":
        if (" is " in padded_query or "is" in query_tokens) and ("==" in normalized_query or "equal" in normalized_query):
            score += 95.0

    # 3. Token overlap with keywords
    topic_words = set()
    for kw in keywords:
        for word in kw.split():
            clean = re.sub(r"[^\w]", "", word.lower())
            if clean and clean not in STOP_WORDS:
                topic_words.add(stem_word(clean))

    for word in title_lower.split():
        clean = re.sub(r"[^\w]", "", word.lower())
        if clean and clean not in STOP_WORDS:
            topic_words.add(stem_word(clean))

    matched_tokens = 0
    for token, stemmed in zip(query_tokens, stemmed_query_tokens):
        if stemmed in topic_words or token in topic_words:
            matched_tokens += 1
            score += 15.0

    # Bonus if query mentions primary topic terms
    topic_id = topic_data["id"]
    if topic_id == "for_loops" and "for" in query_tokens and "loop" in stemmed_query_tokens:
        score += 50.0
    elif topic_id == "while_loops" and "while" in query_tokens:
        score += 50.0
    elif topic_id == "list_comprehensions" and ("comprehension" in stemmed_query_tokens or "comprehensions" in query_tokens):
        score += 60.0
    elif topic_id == "lists_vs_tuples" and ("tuple" in stemmed_query_tokens and "list" in stemmed_query_tokens):
        score += 70.0
    elif topic_id == "lists_vs_dicts" and ("dict" in stemmed_query_tokens or "dictionary" in stemmed_query_tokens) and "list" in stemmed_query_tokens:
        score += 70.0
    elif topic_id == "lists_vs_sets" and ("set" in stemmed_query_tokens and "list" in stemmed_query_tokens):
        score += 70.0
    elif topic_id == "type_conversion" and ("convert" in stemmed_query_tokens or "conversion" in query_tokens or "cast" in query_tokens or "casting" in stemmed_query_tokens):
        score += 105.0
    elif topic_id == "return_values" and "return" in stemmed_query_tokens:
        score += 75.0
    elif topic_id == "file_handling" and ("read" in stemmed_query_tokens or "file" in stemmed_query_tokens):
        score += 40.0
    elif topic_id == "exception_handling" and ("exception" in stemmed_query_tokens or "try" in query_tokens):
        score += 50.0
    elif topic_id == "classes_objects" and ("class" in stemmed_query_tokens or "oop" in query_tokens or "object" in stemmed_query_tokens):
        score += 45.0
    elif topic_id == "modules_packages" and ("module" in stemmed_query_tokens or "package" in stemmed_query_tokens):
        score += 50.0
    elif topic_id == "python_intro" and "python" in query_tokens and ("why" in query_tokens or "what" in query_tokens or "intro" in query_tokens or len(query_tokens) <= 4):
        score += 45.0

    return score

CONFIDENCE_THRESHOLD = 20.0

def query_knowledge_base(question: str) -> Dict[str, Any]:
    """
    Search knowledge base for the question.
    Returns structured result with answer, code example, output, related topics, and confidence.
    """
    clean_q = question.strip()
    norm_q = normalize_text(clean_q)
    tokens = extract_tokens(norm_q)

    # Empty question check
    if not tokens:
        return {
            "topic_id": None,
            "topic_title": None,
            "content": "Please enter a valid Python programming question.",
            "code_example": None,
            "expected_output": None,
            "is_supported": False,
            "related_topics": ["python_intro", "variables_types", "for_loops", "lists_methods"],
            "confidence_score": 0.0
        }

    scored_topics: List[Tuple[str, float]] = []
    for topic_id, topic_data in TOPICS.items():
        score = score_topic(norm_q, tokens, topic_data)
        scored_topics.append((topic_id, score))

    scored_topics.sort(key=lambda x: x[1], reverse=True)
    best_topic_id, best_score = scored_topics[0]

    # If confidence meets threshold
    if best_score >= CONFIDENCE_THRESHOLD:
        topic = TOPICS[best_topic_id]
        
        # Build answer content
        full_content = (
            f"### {topic['title']}\n\n"
            f"**Overview:** {topic['short_explanation']}\n\n"
            f"{topic['detailed_explanation']}"
        )

        # Map related topic titles
        related_titles = [
            TOPICS[rel_id]["title"] for rel_id in topic.get("related_topics", [])
            if rel_id in TOPICS
        ]

        return {
            "topic_id": topic["id"],
            "topic_title": topic["title"],
            "content": full_content,
            "code_example": topic.get("code_example"),
            "expected_output": topic.get("expected_output"),
            "is_supported": True,
            "related_topics": related_titles,
            "confidence_score": round(best_score, 1)
        }

    # Fallback for unsupported questions
    suggested = [
        "What is Python?",
        "Explain lists and tuples.",
        "What is the difference between a list and a dictionary?",
        "Explain for loops with an example.",
        "What are functions in Python?",
        "What is exception handling?",
        "How do I read a text file in Python?"
    ]

    fallback_message = (
        "I'm sorry, that specific question is not available in my current Python knowledge base.\n\n"
        "As PyAssist, I am a specialized developer assistant dedicated to core Python topics "
        "including syntax, data structures (lists, tuples, sets, dicts), control flow, OOP, functions, "
        "exception handling, and file operations.\n\n"
        "Try asking about one of the suggested topics below:"
    )

    return {
        "topic_id": None,
        "topic_title": None,
        "content": fallback_message,
        "code_example": None,
        "expected_output": None,
        "is_supported": False,
        "related_topics": suggested,
        "confidence_score": round(best_score, 1)
    }

def get_all_topics_summary() -> List[Dict[str, str]]:
    """Return summary list of all supported topics."""
    return [
        {"id": t["id"], "title": t["title"], "summary": t["short_explanation"]}
        for t in TOPICS.values()
    ]
