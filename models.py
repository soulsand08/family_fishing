"""
models.py - DBモデル・操作関数
tanka_poolテーブルの操作を担当
"""
from config import get_db_connection

def get_random_tanka():
    """
    tanka_poolからランダムに1件取得
    Returns: (id, content) or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, content FROM tanka_pool ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        return result
    finally:
        cursor.close()
        conn.close()

def delete_tanka(tanka_id):
    """
    指定IDの短歌を削除
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tanka_pool WHERE id = %s", (tanka_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def insert_tanka(content):
    """
    新しい短歌を登録
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tanka_pool(content) VALUES (%s)", (content,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_pool_count():
    """
    プール内の短歌数を取得
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM tanka_pool")
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        conn.close()
