from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from pyassist.app.config import settings
from pyassist.app.database import get_db
from pyassist.app.models import User
from pyassist.app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse
)
from pyassist.app.auth import (
    hash_password,
    verify_password,
    create_user_session,
    revoke_session,
    get_current_user,
    get_session_token_from_request,
    generate_csrf_token,
    check_rate_limit,
    verify_csrf
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def set_auth_cookies(response: Response, session_token: str, csrf_token: str):
    """Set secure, HttpOnly session cookie and client-readable CSRF cookie."""
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/"
    )
    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=False,  # Client JS reads this to include in X-CSRF-Token header
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/"
    )

def clear_auth_cookies(response: Response):
    """Clear session and CSRF cookies."""
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME, path="/")
    response.delete_cookie(key=settings.CSRF_COOKIE_NAME, path="/")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserRegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Register a new user account with Argon2 password hashing and automatic session creation."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not check_rate_limit(f"reg:{client_ip}", max_calls=15, period_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please wait a minute and try again."
        )

    # Check for existing username or email
    existing = db.query(User).filter(
        or_(User.username == user_in.username, User.email == user_in.email)
    ).first()

    if existing:
        if existing.username.lower() == user_in.username.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this username already exists."
            )
        if existing.email.lower() == user_in.email.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists."
            )

    # Hash password with Argon2
    hashed_pw = hash_password(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pw
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically issue session
    session_token, csrf_token = create_user_session(db, user.id)
    set_auth_cookies(response, session_token, csrf_token)

    return user

@router.post("/login", response_model=UserResponse)
def login(
    credentials: UserLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate with username or email and password, establishing an HttpOnly session."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not check_rate_limit(f"login:{client_ip}", max_calls=20, period_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait a minute and try again."
        )

    identifier = credentials.username_or_email.strip().lower()
    user = db.query(User).filter(
        or_(User.username.ilike(identifier), User.email.ilike(identifier))
    ).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )

    session_token, csrf_token = create_user_session(db, user.id)
    set_auth_cookies(response, session_token, csrf_token)

    return user

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _csrf: None = Depends(verify_csrf)
):
    """Revoke session in database and clear cookies."""
    token = get_session_token_from_request(request)
    if token:
        revoke_session(db, token)
    clear_auth_cookies(response)
    return {"message": "Successfully logged out."}

@router.get("/me", response_model=UserResponse)
def get_me(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Return authenticated user profile and refresh CSRF cookie if absent."""
    if not request.cookies.get(settings.CSRF_COOKIE_NAME):
        csrf_token = generate_csrf_token()
        response.set_cookie(
            key=settings.CSRF_COOKIE_NAME,
            value=csrf_token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=False,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            path="/"
        )
    return current_user

@router.get("/csrf")
def get_csrf_token(response: Response, request: Request):
    """Endpoint for initial page load to acquire CSRF cookie."""
    token = request.cookies.get(settings.CSRF_COOKIE_NAME)
    if not token:
        token = generate_csrf_token()
        response.set_cookie(
            key=settings.CSRF_COOKIE_NAME,
            value=token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=False,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            path="/"
        )
    return {"csrf_token": token}
