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
            dbname="postgres",
            user="postgres",
            password="1Dani@2318",
            host="db.gcsqfgmrmskmleazdsze.supabase.co",
            port="5432",
            sslmode="require",
            connect_timeout=10
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