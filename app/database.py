from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import Config

# -------------------------------
# 1️⃣ Ensure database exists
# -------------------------------
def ensure_database():
    default_engine = create_engine(
        f"postgresql+psycopg2://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/postgres",
        isolation_level="AUTOCOMMIT",
        echo=True
    )

    db_name = Config.DB_NAME

    with default_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": db_name}
        ).fetchone()

        if not result:
            print(f"Database '{db_name}' does not exist. Creating it...")
            conn.execute(text(f"CREATE DATABASE {db_name}"))
        else:
            print(f"Database '{db_name}' already exists.")

# Call this at import or in a controlled way
ensure_database()

# -------------------------------
# 2️⃣ Connect to the app database
# -------------------------------
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=True,
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# 3️⃣ Create all tables
# -------------------------------
Base.metadata.create_all(engine)
print("All tables created successfully!")
