"""
Simple script to run Alembic migrations
"""
from alembic.config import Config
from alembic import command

# Create Alembic configuration
alembic_cfg = Config("alembic.ini")

# Run the upgrade command
print("Running database migrations...")
command.upgrade(alembic_cfg, "head")
print("Migrations completed successfully!")
