"""
app.py - メインFlaskアプリケーション
Database_Final-mainのmain.pyに相当
"""
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import get_random_tanka, delete_tanka, insert_tanka, get_pool_count

app = Flask(__name__)

@app.route('/')
def home():
    """ホーム画面"""
    return render_template('home.html')

@app.route('/submit')
def submit():
    """短歌投稿画面"""
    return render_template('submit.html')

@app.route('/exchange', methods=['POST'])
def exchange():
    """
    短歌交換処理
    1. DBからランダム1件取得
    2. 取得した短歌をDBから削除
    3. ユーザーの短歌をDBにINSERT
    4. 取得した短歌をレスポンスとして返す
    """
    # 5行の入力を結合
    lines = []
    for i in range(1, 6):
        line = request.form.get(f'line{i}', '').strip()
        lines.append(line)
    
    user_tanka = '\n'.join(lines)
    
    # 入力チェック
    if not any(lines):
        return render_template('submit.html', error='短歌を入力してください')
    
    # 交換処理
    received = get_random_tanka()
    
    if received is None:
        return render_template('submit.html', error='交換できる短歌がありません')
    
    tanka_id, tanka_content = received
    
    # 取得した短歌を削除
    delete_tanka(tanka_id)
    
    # ユーザーの短歌を登録
    insert_tanka(user_tanka)
    
    return render_template('result.html', received_tanka=tanka_content)

@app.route('/history')
def history():
    """受信履歴画面（LocalStorageから読み込み）"""
    return render_template('history.html')

@app.route('/api/pool_count')
def api_pool_count():
    """プール内の短歌数を返すAPI（デバッグ用）"""
    count = get_pool_count()
    return jsonify({'count': count})

def setup_docker_environment():
    """Dockerコンテナの起動状態を確認し、必要に応じて起動"""
    import subprocess
    import sys
    
    try:
        # Dockerがインストールされているか確認
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("⚠️  Dockerがインストールされていません")
            print("   Docker Desktopをインストールしてください: https://www.docker.com/products/docker-desktop")
            sys.exit(1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Dockerがインストールされていません")
        print("   Docker Desktopをインストールしてください: https://www.docker.com/products/docker-desktop")
        sys.exit(1)
    
    try:
        # tanka_postgresコンテナが起動しているか確認
        result = subprocess.run(['docker', 'ps', '--filter', 'name=tanka_postgres', '--format', '{{.Names}}'],
                              capture_output=True, text=True, timeout=10)
        
        if 'tanka_postgres' not in result.stdout:
            print("🐳 PostgreSQLコンテナを起動中...")
            # docker-compose up -d を実行
            result = subprocess.run(['docker-compose', 'up', '-d'],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✓ PostgreSQLコンテナを起動しました")
            else:
                print(f"✗ コンテナ起動エラー: {result.stderr}")
                sys.exit(1)
        else:
            print("✓ PostgreSQLコンテナは既に起動しています")
    except subprocess.TimeoutExpired:
        print("✗ Dockerコマンドがタイムアウトしました")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Docker環境のセットアップエラー: {e}")
        sys.exit(1)


def wait_for_database(max_retries=30, retry_interval=1):
    """データベース接続を確認し、接続できるまで待機"""
    import time
    from config import get_db_connection
    
    print("🔌 データベース接続を確認中...")
    
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            conn.close()
            print("✓ データベースに接続しました")
            return True
        except Exception as e:
            if i == 0:
                print(f"   データベース起動待機中... (最大{max_retries}秒)")
            time.sleep(retry_interval)
    
    print(f"✗ データベースに接続できませんでした（{max_retries}秒経過）")
    print("   docker-compose logsでログを確認してください")
    return False


if __name__ == '__main__':
    print("=== 匿名短歌交換アプリ起動 ===\n")
    
    # 1. Docker環境のセットアップ
    setup_docker_environment()
    
    # 2. データベース接続確認
    if not wait_for_database():
        import sys
        sys.exit(1)
    
    # 3. データベース初期化（初回のみ）
    print("📊 データベースを初期化中...")
    from init_db import init_database
    init_database()
    
    print("\n✨ アプリケーションを起動します")
    print("   ブラウザで http://localhost:5000 にアクセスしてください\n")
    
    # 4. Flaskアプリ起動
    app.run(debug=True, host='0.0.0.0', port=5000)
