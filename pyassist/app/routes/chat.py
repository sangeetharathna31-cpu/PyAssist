from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from pyassist.app.config import settings
from pyassist.app.database import get_db
from pyassist.app.models import User, Conversation, Message
from pyassist.app.schemas import (
    ChatAskRequest,
    ChatAskResponse,
    MessageResponse
)
from pyassist.app.auth import (
    get_current_user,
    verify_csrf,
    check_rate_limit
)
from pyassist.app.chatbot import query_knowledge_base, get_all_topics_summary

from pyassist.app.gemini_service import generate_gemini_response

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/ask", response_model=ChatAskResponse)
async def ask_question(
    ask_req: ChatAskRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _csrf: None = Depends(verify_csrf)
):
    """
    Process natural-language Python question across 5 functional AI modes:
    - ask: General Python programming Q&A
    - generate: Python code synthesis with usage example
    - debug: Traceback and bug diagnosis with root cause & fix
    - explain: Algorithm and code breakdown with complexity
    - review: Comprehensive code quality, PEP 8, and security review
    """
    # Rate limit per user
    if not check_rate_limit(f"chat:{current_user.id}", max_calls=40, period_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit reached. Please wait a moment before asking another question."
        )

    mode = ask_req.mode or "ask"

    # Validate or create conversation
    conversation: Conversation
    if ask_req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == ask_req.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or does not belong to you."
            )
    else:
        # Create new conversation with clean title
        title_text = ask_req.question.strip()
        if len(title_text) > 40:
            title_text = title_text[:37].rsplit(" ", 1)[0] + "..."
        mode_prefix = f"[{mode.capitalize()}] " if mode != "ask" else ""
        conversation = Conversation(
            user_id=current_user.id,
            title=f"{mode_prefix}{title_text}"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 1. Save user question message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=ask_req.question,
        topic_id=f"mode:{mode}",
        is_supported=True
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 2. Try genuine Gemini API reasoning
    bot_content = ""
    code_example = None
    expected_output = None
    topic_id = f"ai_{mode}"
    is_supported = True
    confidence_score = 100.0
    related_topics = []
    model_used = None

    # Check if Gemini API key is configured
    if settings.GEMINI_API_KEY:
        ai_result = await generate_gemini_response(ask_req.question, mode=mode)
        if ai_result["success"]:
            bot_content = ai_result["content"]
            code_example = ai_result["code_example"]
            expected_output = ai_result["expected_output"]
            model_used = ai_result["model_used"]
            topic_id = f"gemini_{mode}"
            is_supported = True
            confidence_score = 99.0
        else:
            # If all Gemini models failed or quota exceeded
            logger_msg = ai_result.get("message", "AI service unavailable.")
            # Fall back to local knowledge base if ask mode, or return diagnostic
            if mode == "ask":
                kb_result = query_knowledge_base(ask_req.question)
                bot_content = kb_result["content"]
                code_example = kb_result["code_example"]
                expected_output = kb_result["expected_output"]
                topic_id = kb_result["topic_id"]
                is_supported = kb_result["is_supported"]
                related_topics = kb_result["related_topics"]
                confidence_score = kb_result["confidence_score"]
            else:
                bot_content = f"Gemini is unavailable: {logger_msg}"
                topic_id = None
                is_supported = False
                confidence_score = 0.0
    else:
        if mode == "ask":
            # General Q&A remains available from the deterministic local knowledge base.
            kb_result = query_knowledge_base(ask_req.question)
            bot_content = kb_result["content"]
            code_example = kb_result["code_example"]
            expected_output = kb_result["expected_output"]
            topic_id = kb_result["topic_id"]
            is_supported = kb_result["is_supported"]
            related_topics = kb_result["related_topics"]
            confidence_score = kb_result["confidence_score"]
        else:
            # Do not claim a KB response is code generation/debugging/review.
            bot_content = (
                "This mode requires Gemini, but no server-side Gemini API key is configured. "
                "Ask mode can still use the local Python knowledge base."
            )
            topic_id = None
            is_supported = False
            confidence_score = 0.0

    # 3. Save assistant response message
    bot_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=bot_content,
        code_example=code_example,
        expected_output=expected_output,
        topic_id=topic_id,
        is_supported=is_supported
    )
    db.add(bot_msg)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bot_msg)

    user_resp = MessageResponse.model_validate(user_msg)
    user_resp.mode = mode

    bot_resp = MessageResponse.model_validate(bot_msg)
    bot_resp.mode = mode
    bot_resp.model_used = model_used

    return ChatAskResponse(
        conversation_id=conversation.id,
        conversation_title=conversation.title,
        user_message=user_resp,
        bot_message=bot_resp,
        related_topics=related_topics,
        confidence_score=confidence_score,
        mode=mode,
        model_used=model_used
    )

@router.get("/topics")
def list_topics():
    """Return overview of all supported topics and categories."""
    return get_all_topics_summary()
