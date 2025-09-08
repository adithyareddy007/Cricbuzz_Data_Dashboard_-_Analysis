from sqlalchemy import create_engine
import psycopg2

def get_connection():
    try:
        # Update with your credentials
        engine = create_engine(
            "postgresql+psycopg2://postgres:adi1234@localhost:5432/cricbuzz_db"
        )
        return engine.connect()
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None
