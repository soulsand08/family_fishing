"""
config.py - DB接続設定
Database_Final-mainのvariables.pyに相当
"""
import os
from dotenv import load_dotenv
import psycopg2

# .envから環境変数を読み込み
load_dotenv()

# DB接続情報
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'tanka_db'),
    'user': os.getenv('DB_USER', 'tanka_user'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

def get_db_connection():
    """PostgreSQL接続を取得"""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn
