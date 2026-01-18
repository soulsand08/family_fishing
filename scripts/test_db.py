import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'tanka_db'),
    'user': os.getenv('DB_USER', 'tanka_user'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

def test():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1")
        print("Basic SQL: OK")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("pgvector check: OK")
        cursor.execute("SELECT id, content FROM tanka_pool LIMIT 1")
        print("tanka_pool check: OK")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test()
