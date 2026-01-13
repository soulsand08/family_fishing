"""
init_db.py - DB初期化スクリプト
テーブル作成とダミーデータ投入
Foreign Key, JOIN, SubQueryを使用する本格的なDB設計
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_db_connection

# ダミー短歌データ（カテゴリ情報付き）
DUMMY_TANKAS = [
    ("古池や\n蛙飛び込む\n水の音\n静けさに\n響く波紋", ["夏", "自然"]),
    ("春過ぎて\n夏来にけらし\n白妙の\n衣干すてふ\n天の香具山", ["夏", "自然"]),
    ("秋の田の\nかりほの庵の\n苫をあらみ\nわが身世にふる\n露にぬれつつ", ["秋", "自然"]),
    ("花の色は\nうつりにけりな\nいたづらに\nわが身世にふる\nながめせしまに", ["春", "恋"]),
    ("月見れば\nちぢに物こそ\n悲しけれ\nわが身一つの\n秋にはあらねど", ["秋", "自然"]),
    ("山里は\n冬ぞ寂しさ\nまさりける\n人目も草も\nかれぬと思へば", ["冬", "自然"]),
    ("風そよぐ\n楢の小川の\n夕暮れは\nみそぎぞ夏の\nしるしなりける", ["夏", "自然"]),
    ("忘れじの\nゆく末までは\nかたければ\n今日を限りの\n命ともがな", ["恋"]),
    ("瀬をはやみ\n岩にせかるる\n滝川の\nわれても末に\nあはむとぞ思ふ", ["恋", "自然"]),
    ("もろともに\nあはれと思へ\n山桜\n花よりほかに\n知る人もなし", ["春", "自然"])
]

# カテゴリマスタ
CATEGORIES = [
    ("春", "春の季語を含む短歌"),
    ("夏", "夏の季語を含む短歌"),
    ("秋", "秋の季語を含む短歌"),
    ("冬", "冬の季語を含む短歌"),
    ("恋", "恋愛をテーマにした短歌"),
    ("自然", "自然をテーマにした短歌")
]

def init_database():
    """データベースを初期化"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=" * 50)
        print("データベース初期化開始")
        print("=" * 50)
        
        # 1. usersテーブル作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("[v] usersテーブルを作成しました")
        
        # 2. categoriesテーブル作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()
        print("[v] categoriesテーブルを作成しました")
        
        # 3. tanka_poolテーブル作成（Foreign Key追加）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tanka_pool (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                exchange_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("[v] tanka_poolテーブルを作成しました（Foreign Key: user_id）")
        
        # 4. exchange_historyテーブル作成（Foreign Key使用）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_history (
                exchange_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                given_tanka_id INTEGER,
                given_tanka_content TEXT NOT NULL,
                received_tanka_id INTEGER,
                received_tanka_content TEXT NOT NULL,
                exchanged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("[v] exchange_historyテーブルを作成しました（Foreign Key: user_id）")
        
        # 5. tanka_categoriesテーブル作成（多対多関係、複数Foreign Key）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tanka_categories (
                tanka_id INTEGER REFERENCES tanka_pool(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(category_id) ON DELETE CASCADE,
                PRIMARY KEY (tanka_id, category_id)
            )
        ''')
        conn.commit()
        print("[v] tanka_categoriesテーブルを作成しました（Foreign Key: tanka_id, category_id）")
        
        # 6. カテゴリデータ投入
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        if count == 0:
            for name, description in CATEGORIES:
                cursor.execute(
                    "INSERT INTO categories(name, description) VALUES (%s, %s)",
                    (name, description)
                )
            conn.commit()
            print(f"[v] カテゴリデータを{len(CATEGORIES)}件投入しました")
        else:
            print(f"[v] 既存カテゴリあり（{count}件）- スキップ")
        
        # 7. 短歌データ投入
        cursor.execute("SELECT COUNT(*) FROM tanka_pool")
        count = cursor.fetchone()[0]
        if count == 0:
            for tanka_content, category_names in DUMMY_TANKAS:
                # 短歌を挿入
                cursor.execute(
                    "INSERT INTO tanka_pool(content) VALUES (%s) RETURNING id",
                    (tanka_content,)
                )
                tanka_id = cursor.fetchone()[0]
                
                # カテゴリとの関連付け
                for category_name in category_names:
                    cursor.execute(
                        "SELECT category_id FROM categories WHERE name = %s",
                        (category_name,)
                    )
                    category_id = cursor.fetchone()[0]
                    cursor.execute(
                        "INSERT INTO tanka_categories(tanka_id, category_id) VALUES (%s, %s)",
                        (tanka_id, category_id)
                    )
            
            conn.commit()
            print(f"[v] ダミー短歌を{len(DUMMY_TANKAS)}件投入しました")
            print("[v] 短歌とカテゴリの関連付けを完了しました")
        else:
            print(f"[v] 既存短歌あり（{count}件）- スキップ")
        
        print("=" * 50)
        print("データベース初期化完了")
        print("=" * 50)
        
        # テーブル情報を表示
        print("\n【作成されたテーブル】")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}")
        
        # Foreign Key制約を表示
        print("\n【Foreign Key制約】")
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}.{row[1]} → {row[2]}.{row[3]}")
            
    except Exception as e:
        print(f"[x] エラー: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_database()
