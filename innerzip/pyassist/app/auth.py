import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from pyassist.app.config import settings
from pyassist.app.database import get_db
from pyassist.app.models import User, UserSession

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2 hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False

def generate_session_token() -> str:
    """Generate cryptographically strong random token."""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Generate SHA-256 hash of a session token for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_csrf_token() -> str:
    """Generate cryptographically random CSRF token."""
    return secrets.token_hex(24)

# In-memory rate limiter per IP/identifier: {key: [(timestamp)]}
_rate_limits: Dict[str, list] = {}

def check_rate_limit(key: str, max_calls: int, period_seconds: int = 60) -> bool:
    """Simple in-memory sliding window rate limiter."""
    if settings.APP_ENV == "test":
        return True
    now = time.time()
    cutoff = now - period_seconds
    timestamps = _rate_limits.setdefault(key, [])
    # Remove older entries
    _rate_limits[key] = [t for t in timestamps if t > cutoff]
    if len(_rate_limits[key]) >= max_calls:
        return False
    _rate_limits[key].append(now)
    return True

def reset_rate_limits():
    """Reset all in-memory rate limits."""
    _rate_limits.clear()

def get_session_token_from_request(request: Request) -> Optional[str]:
    """Extract session token from HttpOnly cookie or Authorization header fallback."""
    cookie_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if cookie_token:
        return cookie_token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Authenticate current user using session cookie."""
    token = get_session_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in."
        )

    token_hash = hash_token(token)
    now = datetime.utcnow()

    session_record = (
        db.query(UserSession)
        .filter(UserSession.token_hash == token_hash, UserSession.expires_at > now)
        .first()
    )

    if not session_record or not session_record.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again."
        )

    return session_record.user

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Return user if logged in, otherwise None."""
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None

def verify_csrf(request: Request) -> None:
    """
    CSRF verification for state-changing requests using cookie authentication.
    Compares X-CSRF-Token header with the pyassist_csrf cookie.
    If the request is authenticated via Bearer token header, CSRF is not required.
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    # If auth header is explicitly provided without session cookie, skip CSRF
    auth_header = request.headers.get("Authorization")
    cookie_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if auth_header and not cookie_token:
        return

    csrf_cookie = request.cookies.get(settings.CSRF_COOKIE_NAME)
    csrf_header = request.headers.get("X-CSRF-Token")

    if not csrf_cookie or not csrf_header or not hmac.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing CSRF token."
        )

def create_user_session(db: Session, user_id: int) -> Tuple[str, str]:
    """Create a new session record in DB and return (raw_session_token, csrf_token)."""
    raw_token = generate_session_token()
    token_h = hash_token(raw_token)
    csrf_token = generate_csrf_token()
    expires_at = datetime.utcnow() + timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)

    session_record = UserSession(
        user_id=user_id,
        token_hash=token_h,
        expires_at=expires_at
    )
    db.add(session_record)
    db.commit()

    return raw_token, csrf_token

def revoke_session(db: Session, raw_token: str) -> None:
    """Revoke session from database."""
    token_h = hash_token(raw_token)
    db.query(UserSession).filter(UserSession.token_hash == token_h).delete()
    db.commit()
