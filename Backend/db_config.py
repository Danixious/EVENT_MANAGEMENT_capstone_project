import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    try:
        print("🚨 TRYING DIRECT CONNECTION...")

        conn = psycopg2.connect(
        "postgresql://postgres.gcsqfgmrmskmleazdsze:1Dani%402318@aws-1-ap-south-1.pooler.supabase.com:6543/postgres",
        sslmode="require"
)

        print("✅ CONNECTION SUCCESS")
        return conn

    except Exception as e:
        print("❌ FULL ERROR:", repr(e))
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

    print("DEBUG DB URL:", DATABASE_URL)