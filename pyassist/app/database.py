from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pyassist.app.config import settings

# SQLite requires check_same_thread=False for multiple threads in FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables in the database and seed initial demo user."""
    Base.metadata.create_all(bind=engine)
    
    # Optional seed for demo convenience
    from pyassist.app.models import User
    from pyassist.app.auth import hash_password
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "demo_user").first():
            demo = User(
                username="demo_user",
                email="demo@pyassist.dev",
                password_hash=hash_password("Password123")
            )
            db.add(demo)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
