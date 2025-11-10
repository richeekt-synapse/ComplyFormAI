from sqlalchemy import create_engine, text

# CORRECT connection string from Supabase
connection_url = "postgresql://postgres.lfizixmiqrspdskubdyj:sgnAdmin11%24%24@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

print("="*70)
print("Testing CORRECT Supabase Session Pooler Connection")
print("="*70)

try:
    engine = create_engine(connection_url, pool_pre_ping=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        
        print("✅ ✅ ✅ CONNECTION SUCCESSFUL! ✅ ✅ ✅")
        print(f"\nPostgreSQL: {version[:80]}...")
        
        # Count tables
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        count = result.fetchone()[0]
        print(f"\n📊 Tables in database: {count}")
        
        if count > 0:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                LIMIT 10
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"\nFirst 10 tables:")
            for table in tables:
                print(f"  ✓ {table}")
        
        print(f"\n{'='*70}")
        print("🎉 Your Supabase database is connected and working!")
        print(f"{'='*70}\n")
        
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")