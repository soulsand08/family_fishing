"""
models.py - DBモデル・操作関数
tanka_poolテーブルの操作を担当
Foreign Key, JOIN, SubQueryを使用した高度なSQL機能を実装
"""
from config import get_db_connection
import uuid

# ==================== ユーザー管理 ====================

def get_or_create_user(session_id):
    """
    セッションIDからユーザーを取得、存在しなければ作成
    Returns: user_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 既存ユーザーを検索
        cursor.execute("SELECT user_id FROM users WHERE session_id = %s", (session_id,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            # 新規ユーザー作成
            cursor.execute(
                "INSERT INTO users(session_id) VALUES (%s) RETURNING user_id",
                (session_id,)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
    finally:
        cursor.close()
        conn.close()

# ==================== 短歌操作（基本） ====================

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

def insert_tanka(content, user_id=None):
    """
    新しい短歌を登録
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tanka_pool(content, user_id) VALUES (%s, %s) RETURNING id",
            (content, user_id)
        )
        tanka_id = cursor.fetchone()[0]
        conn.commit()
        return tanka_id
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

# ==================== JOIN使用 ====================

def get_tankas_by_category(category_name):
    """
    カテゴリ別に短歌を取得（JOIN使用）
    
    SQL要素: INNER JOIN（3テーブル結合）
    tanka_pool JOIN tanka_categories JOIN categories
    
    Returns: [(tanka_id, content, category_name), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                tp.id,
                tp.content,
                c.name as category_name
            FROM tanka_pool tp
            INNER JOIN tanka_categories tc ON tp.id = tc.tanka_id
            INNER JOIN categories c ON tc.category_id = c.category_id
            WHERE c.name = %s
            ORDER BY tp.created_at DESC
        """, (category_name,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_tanka_with_categories(tanka_id):
    """
    短歌とそのカテゴリを取得（JOIN使用）
    
    SQL要素: LEFT JOIN, GROUP BY, STRING_AGG
    
    Returns: (tanka_id, content, categories_csv)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                tp.id,
                tp.content,
                STRING_AGG(c.name, ', ') as categories
            FROM tanka_pool tp
            LEFT JOIN tanka_categories tc ON tp.id = tc.tanka_id
            LEFT JOIN categories c ON tc.category_id = c.category_id
            WHERE tp.id = %s
            GROUP BY tp.id, tp.content
        """, (tanka_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_all_tankas_with_categories():
    """
    全短歌をカテゴリ情報付きで取得（JOIN使用）
    
    SQL要素: LEFT JOIN, GROUP BY, STRING_AGG
    
    Returns: [(tanka_id, content, categories_csv, exchange_count), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                tp.id,
                tp.content,
                STRING_AGG(c.name, ', ') as categories,
                tp.exchange_count
            FROM tanka_pool tp
            LEFT JOIN tanka_categories tc ON tp.id = tc.tanka_id
            LEFT JOIN categories c ON tc.category_id = c.category_id
            GROUP BY tp.id, tp.content, tp.exchange_count
            ORDER BY tp.created_at DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# ==================== SubQuery使用 ====================

def get_popular_tankas(limit=10):
    """
    人気の短歌ランキング（SubQuery使用）
    
    SQL要素: SubQuery, LEFT JOIN, COALESCE, ORDER BY
    
    exchange_historyから交換回数をカウントし、
    SubQueryの結果を使って人気順にソート
    
    Returns: [(tanka_id, content, exchange_count, categories), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                tp.id,
                tp.content,
                COALESCE(
                    (SELECT COUNT(*) 
                     FROM exchange_history eh 
                     WHERE eh.received_tanka_id = tp.id),
                    0
                ) as exchange_count,
                STRING_AGG(c.name, ', ') as categories
            FROM tanka_pool tp
            LEFT JOIN tanka_categories tc ON tp.id = tc.tanka_id
            LEFT JOIN categories c ON tc.category_id = c.category_id
            GROUP BY tp.id, tp.content
            ORDER BY exchange_count DESC
            LIMIT %s
        """, (limit,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_category_stats():
    """
    カテゴリ別統計（SubQuery使用）
    
    SQL要素: SubQuery, JOIN, GROUP BY, COUNT
    
    Returns: [(category_name, tanka_count, description), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.name,
                (SELECT COUNT(*) 
                 FROM tanka_categories tc 
                 WHERE tc.category_id = c.category_id) as tanka_count,
                c.description
            FROM categories c
            ORDER BY tanka_count DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# ==================== 交換履歴（Foreign Key活用） ====================

def record_exchange(user_id, given_tanka_id, given_content, received_tanka_id, received_content):
    """
    交換履歴を記録（Foreign Key制約あり）
    
    SQL要素: Foreign Key制約による参照整合性
    user_id は users テーブルに存在する必要がある
    
    Returns: exchange_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO exchange_history(
                user_id, 
                given_tanka_id, 
                given_tanka_content,
                received_tanka_id,
                received_tanka_content
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING exchange_id
        """, (user_id, given_tanka_id, given_content, received_tanka_id, received_content))
        exchange_id = cursor.fetchone()[0]
        
        # exchange_countをインクリメント
        cursor.execute("""
            UPDATE tanka_pool 
            SET exchange_count = exchange_count + 1 
            WHERE id = %s
        """, (received_tanka_id,))
        
        conn.commit()
        return exchange_id
    finally:
        cursor.close()
        conn.close()

def get_user_exchange_history(user_id, limit=20):
    """
    ユーザーの交換履歴を取得
    
    SQL要素: Foreign Key, ORDER BY, LIMIT
    
    Returns: [(exchange_id, given_content, received_content, exchanged_at), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                exchange_id,
                given_tanka_content,
                received_tanka_content,
                exchanged_at
            FROM exchange_history
            WHERE user_id = %s
            ORDER BY exchanged_at DESC
            LIMIT %s
        """, (user_id, limit))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# ==================== 複雑なJOIN ====================

def get_user_exchange_stats(user_id):
    """
    ユーザーの交換統計（複数テーブルのJOIN）
    
    SQL要素: JOIN, COUNT, MIN, MAX, GROUP BY
    users JOIN exchange_history で統計を取得
    
    Returns: {
        'total_exchanges': int,
        'first_exchange': datetime,
        'last_exchange': datetime,
        'session_id': str
    }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                u.session_id,
                COUNT(eh.exchange_id) as total_exchanges,
                MIN(eh.exchanged_at) as first_exchange,
                MAX(eh.exchanged_at) as last_exchange
            FROM users u
            LEFT JOIN exchange_history eh ON u.user_id = eh.user_id
            WHERE u.user_id = %s
            GROUP BY u.user_id, u.session_id
        """, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return {
                'session_id': result[0],
                'total_exchanges': result[1],
                'first_exchange': result[2],
                'last_exchange': result[3]
            }
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_categories():
    """
    全カテゴリを取得
    
    Returns: [(category_id, name, description), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT category_id, name, description FROM categories ORDER BY name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
