"""Test database connection"""
import os
from sqlalchemy import create_engine, text

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5432/ComplyFormAI"
)

print(f"Testing connection to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✓ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test if tables exist
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public';"
        ))
        tables = result.fetchall()
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nPlease check:")
    print("1. PostgreSQL is running")
    print("2. Database 'complyform' exists")
    print("3. Username and password are correct")
    print("4. Host and port are correct")