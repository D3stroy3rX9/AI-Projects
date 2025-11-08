"""
Create database tables directly without Alembic
"""
from sqlalchemy import create_engine, text
from db.database import Base
from db.models import Analysis, Model, TrainingData, AnalyticsSummary
from config import settings

print("Creating database tables...")

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Create all tables
Base.metadata.create_all(bind=engine)

print("✓ All tables created successfully!")

# Enable TimescaleDB extension and create hypertable
print("\nSetting up TimescaleDB...")
try:
    with engine.connect() as conn:
        # Enable TimescaleDB extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
        conn.commit()

        # Convert analysis table to hypertable
        conn.execute(text("""
            SELECT create_hypertable(
                'analysis',
                'analyzed_at',
                if_not_exists => TRUE,
                migrate_data => TRUE
            );
        """))
        conn.commit()
        print("✓ TimescaleDB hypertable created successfully!")
except Exception as e:
    print(f"⚠ TimescaleDB setup skipped (not critical): {e}")

print("\n✅ Database setup complete! You can now run seed.py")
