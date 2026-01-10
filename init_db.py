"""
init_db.py - DB初期化スクリプト
テーブル作成とダミーデータ投入
"""
from config import get_db_connection

# ダミー短歌データ
DUMMY_TANKAS = [
    "古池や\n蛙飛び込む\n水の音\n静けさに\n響く波紋",
    "春過ぎて\n夏来にけらし\n白妙の\n衣干すてふ\n天の香具山",
    "秋の田の\nかりほの庵の\n苫をあらみ\nわが衣手は\n露にぬれつつ",
    "花の色は\nうつりにけりな\nいたづらに\nわが身世にふる\nながめせしまに",
    "月見れば\nちぢに物こそ\n悲しけれ\nわが身一つの\n秋にはあらねど",
    "山里は\n冬ぞ寂しさ\nまさりける\n人目も草も\nかれぬと思へば",
    "風そよぐ\n楢の小川の\n夕暮れは\nみそぎぞ夏の\nしるしなりける",
    "忘れじの\nゆく末までは\nかたければ\n今日を限りの\n命ともがな",
    "瀬をはやみ\n岩にせかるる\n滝川の\nわれても末に\nあはむとぞ思ふ",
    "もろともに\nあはれと思へ\n山桜\n花よりほかに\n知る人もなし"
]

def init_database():
    """データベースを初期化"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # テーブル作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tanka_pool (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("✓ tanka_poolテーブルを作成しました")
        
        # 既存データ確認
        cursor.execute("SELECT COUNT(*) FROM tanka_pool")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # ダミーデータ投入
            for tanka in DUMMY_TANKAS:
                cursor.execute("INSERT INTO tanka_pool(content) VALUES (%s)", (tanka,))
            conn.commit()
            print(f"✓ ダミー短歌を{len(DUMMY_TANKAS)}件投入しました")
        else:
            print(f"✓ 既存データあり（{count}件）- ダミー投入はスキップ")
            
    except Exception as e:
        print(f"✗ エラー: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=== DB初期化開始 ===")
    init_database()
    print("=== DB初期化完了 ===")
