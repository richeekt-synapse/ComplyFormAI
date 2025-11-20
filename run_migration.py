"""
Migration script to add contractors_using_count column to subcontractor_directory table
"""
import psycopg

from app.config import settings

def run_migration():
    """Run the migration to add contractors_using_count column"""

    # Parse the database URL
    db_url = settings.DATABASE_URL

    # Connect to the database
    try:
        print("Connecting to database...")
        conn = psycopg.connect(db_url)
        cursor = conn.cursor()

        print("Running migration: Adding contractors_using_count column...")

        # Add the column
        cursor.execute("""
            ALTER TABLE subcontractor_directory
            ADD COLUMN IF NOT EXISTS contractors_using_count INTEGER DEFAULT 0;
        """)

        # Update existing records
        cursor.execute("""
            UPDATE subcontractor_directory
            SET contractors_using_count = 0
            WHERE contractors_using_count IS NULL;
        """)

        # Commit the changes
        conn.commit()

        print("[SUCCESS] Migration completed successfully!")
        print("[SUCCESS] Added contractors_using_count column to subcontractor_directory table")

        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'subcontractor_directory'
            AND column_name = 'contractors_using_count';
        """)

        result = cursor.fetchone()
        if result:
            print(f"[SUCCESS] Verified column exists: {result[0]} ({result[1]}) with default {result[2]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] Error running migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    run_migration()
