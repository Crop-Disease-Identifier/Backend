import os
import dotenv
from sqlalchemy import create_engine, text

dotenv.load_dotenv()

DATABASE_URL = os.getenv("database_url")
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

with engine.connect() as conn:
    # Alter the fullname column to allow NULL
    conn.execute(text("ALTER TABLE users ALTER COLUMN fullname DROP NOT NULL"))
    conn.commit()
    print("✓ Migration completed: fullname column now allows NULL values")
