"""
Migration script to add category_breakdown column to bid_subcontractors table
"""
import os
import sys
from dotenv import load_dotenv
import psycopg

# Set UTF-8 encoding for print
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("Error: DATABASE_URL not found in environment variables")
    exit(1)

print(f"Connecting to database using connection string...")
print(f"URL: {database_url[:50]}...")  # Show only first 50 chars for security

try:
    # Connect to the database using connection string
    conn = psycopg.connect(database_url, autocommit=False)
    cursor = conn.cursor()

    print("\nRunning migration...")

    # Read the SQL migration file
    with open('add_category_breakdown.sql', 'r') as f:
        sql = f.read()

    # Execute the migration
    cursor.execute(sql)

    # Commit the transaction
    conn.commit()

    print("SUCCESS: Migration completed successfully!")

    # Verify the column was added
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'bid_subcontractors' AND column_name = 'category_breakdown';
    """)

    result = cursor.fetchone()
    if result:
        print(f"\nVerification successful:")
        print(f"  Column name: {result[0]}")
        print(f"  Data type: {result[1]}")
        print(f"  Nullable: {result[2]}")
    else:
        print("\nWARNING: Column not found after migration")

    # Check if index was created
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'bid_subcontractors' AND indexname = 'idx_bid_subcontractors_category_breakdown';
    """)

    index_result = cursor.fetchone()
    if index_result:
        print(f"\nIndex created: {index_result[0]}")

    cursor.close()
    conn.close()

    print("\nAll done! The database has been updated successfully.")

except psycopg.Error as e:
    print(f"\nDatabase error: {e}")
    try:
        if 'conn' in locals():
            conn.rollback()
    except:
        pass
    exit(1)
except Exception as e:
    print(f"\nError: {e}")
    try:
        if 'conn' in locals():
            conn.rollback()
    except:
        pass
    exit(1)
