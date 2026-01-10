"""
verify_db.py - データベース検証スクリプト
Foreign Key, JOIN, SubQueryの動作確認
"""
from config import get_db_connection

def verify_database():
    """データベースの状態を検証"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)
        
        # 1. テーブル一覧
        print("\n[1] Tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}")
        
        # 2. Foreign Key制約
        print("\n[2] Foreign Key Constraints:")
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
            print(f"  - {row[0]}.{row[1]} -> {row[2]}.{row[3]}")
        
        # 3. データ件数
        print("\n[3] Record Counts:")
        tables = ['users', 'categories', 'tanka_pool', 'tanka_categories', 'exchange_history']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} records")
        
        # 4. カテゴリ一覧
        print("\n[4] Categories:")
        cursor.execute("SELECT name, description FROM categories ORDER BY name")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        # 5. JOIN テスト（カテゴリ別短歌数）
        print("\n[5] JOIN Test - Tankas per Category:")
        cursor.execute("""
            SELECT 
                c.name,
                COUNT(tc.tanka_id) as tanka_count
            FROM categories c
            LEFT JOIN tanka_categories tc ON c.category_id = tc.category_id
            GROUP BY c.name
            ORDER BY tanka_count DESC
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} tankas")
        
        # 6. SubQuery テスト（人気短歌）
        print("\n[6] SubQuery Test - Popular Tankas:")
        cursor.execute("""
            SELECT 
                tp.id,
                LEFT(tp.content, 30) as preview,
                COALESCE(
                    (SELECT COUNT(*) 
                     FROM exchange_history eh 
                     WHERE eh.received_tanka_id = tp.id),
                    0
                ) as exchange_count
            FROM tanka_pool tp
            ORDER BY exchange_count DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            preview = row[1].replace('\n', ' ')
            print(f"  - ID {row[0]}: '{preview}...' ({row[2]} exchanges)")
        
        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE - All SQL features working!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verify_database()
