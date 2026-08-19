from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

# 1. Connection URL to Docker Database
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 2. Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Create database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class to be inherited by all Models
Base = declarative_base()

# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================

# Function to initialize database (creates tables automatically if missing)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency Injection function for API Routers
def get_db():
    db = SessionLocal() # Open database connection
    try:
        yield db        # Pass connection session to router -> service -> repository
    finally:
        db.close()      # Automatically close connection session when request finishes