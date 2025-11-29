"""
Simple database initialization script (Alternative to Alembic)
Run this to create database tables without using migrations
"""
from db.database import engine, init_db, drop_db
from db.models import Base
import sys


def main():
    """Initialize database tables"""
    print("=" * 50)
    print("Database Initialization Script")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        print("\n⚠️  WARNING: This will drop all existing tables!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() == "yes":
            drop_db()
            print("✅ All tables dropped")
        else:
            print("❌ Operation cancelled")
            return

    print("\n📊 Creating database tables...")

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")

        # Show created tables
        print("\n📋 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

        print("\n" + "=" * 50)
        print("✅ Database initialization complete!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check PostgreSQL is running: docker-compose ps")
        print("2. Check DATABASE_URL in .env file")
        print("3. Verify PostgreSQL credentials")
        sys.exit(1)


if __name__ == "__main__":
    main()
