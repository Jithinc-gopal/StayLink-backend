import time
import psycopg2
import os

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "StayLinkDB")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345")

print("⏳ Waiting for PostgreSQL...")

while True:
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        conn.close()
        print("✅ PostgreSQL is ready!")
        break
    except psycopg2.OperationalError:
        print("🔄 Not ready yet, retrying in 2s...")
        time.sleep(2)