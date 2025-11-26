from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv
import os

dotenv.load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("database_url")

# Auto-detect SSL mode based on database host
# If using remote database (Neon, AWS RDS, Railway), require SSL
# If using localhost, disable SSL
ssl_mode = os.getenv("DB_SSL_MODE")
if ssl_mode is None:
    # Auto-detect: use require for remote databases, disable for localhost
    if SQLALCHEMY_DATABASE_URL and ("localhost" in SQLALCHEMY_DATABASE_URL or "127.0.0.1" in SQLALCHEMY_DATABASE_URL):
        ssl_mode = "disable"
    else:
        ssl_mode = "require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"sslmode": ssl_mode},
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections every hour
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
