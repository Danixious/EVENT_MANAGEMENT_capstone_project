import psycopg2
import os
from dotenv import load_dotenv

def get_connection():
    try:
        print("🚀 Connecting to Supabase via Pooler...")

        conn = psycopg2.connect(
            "postgresql://postgres.gcsqfgmrmskmleazdsze:icggFhCibEvJQtOQ@aws-1-ap-south-1.pooler.supabase.com:6543/postgres",
            sslmode="require"
        )

        print("✅ Connected to Supabase!")
        return conn

    except Exception as e:
        print("❌ Connection Error:", repr(e))
        return None


# Main test block
if __name__ == "__main__":
    conn = get_connection()

    if conn:
        print("✅ Connected to Supabase!")

        # Check DB version
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print("📌 DB Version:", cur.fetchone())

        cur.close()
        conn.close()

    else:
        print("❌ Failed to connect to database.")

