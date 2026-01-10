"""
migrate_db.py - データベースマイグレーションスクリプト
既存のtanka_poolテーブルにexchange_countカラムを追加
"""
from config import get_db_connection

def migrate_database():
    """既存テーブルにカラムを追加"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("DATABASE MIGRATION")
        print("=" * 60)
        
        # exchange_countカラムが存在するか確認
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tanka_pool' AND column_name = 'exchange_count'
        """)
        
        if cursor.fetchone() is None:
            print("\n[1] Adding exchange_count column to tanka_pool...")
            cursor.execute("""
                ALTER TABLE tanka_pool 
                ADD COLUMN exchange_count INTEGER DEFAULT 0
            """)
            conn.commit()
            print("✓ exchange_count column added successfully")
        else:
            print("\n✓ exchange_count column already exists")
        
        # user_idカラムが存在するか確認
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tanka_pool' AND column_name = 'user_id'
        """)
        
        if cursor.fetchone() is None:
            print("\n[2] Adding user_id column to tanka_pool...")
            cursor.execute("""
                ALTER TABLE tanka_pool 
                ADD COLUMN user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL
            """)
            conn.commit()
            print("✓ user_id column added successfully")
        else:
            print("✓ user_id column already exists")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        
        # テーブル構造を表示
        print("\n[tanka_pool table structure]")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'tanka_pool'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_database()
