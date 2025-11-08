"""
Simple script to run Alembic migrations
"""
import subprocess
import sys

# Run alembic upgrade head
result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"])
sys.exit(result.returncode)
