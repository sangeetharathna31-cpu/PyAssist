import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not USERNAME_REGEX.match(v):
            raise ValueError("Username must be 3-30 characters long and contain only letters, numbers, and underscores.")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email address format.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number.")
        return v


class UserLoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


VALID_MODES = {"ask", "generate", "debug", "explain", "review"}

class ChatAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[int] = None
    mode: str = Field(default="ask")

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty or whitespace only.")
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_MODES:
            raise ValueError(f"Invalid mode '{v}'. Must be one of: {', '.join(sorted(VALID_MODES))}")
        return v


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    code_example: Optional[str] = None
    expected_output: Optional[str] = None
    topic_id: Optional[str] = None
    is_supported: bool = True
    created_at: datetime
    mode: Optional[str] = "ask"
    model_used: Optional[str] = None


class ChatAskResponse(BaseModel):
    conversation_id: int
    conversation_title: str
    user_message: MessageResponse
    bot_message: MessageResponse
    related_topics: List[str] = []
    confidence_score: float = 0.0
    mode: str = "ask"
    model_used: Optional[str] = None


class ConversationSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: Optional[str] = None


class ConversationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    database: str
    timestamp: datetime
