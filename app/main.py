"""
app.py - メインFlaskアプリケーション
Database_Final-mainのmain.pyに相当
Foreign Key, JOIN, SubQueryを使用した高度な機能を実装
"""
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from .models import (
    get_random_tanka, delete_tanka, insert_tanka, get_pool_count,
    get_or_create_user, record_exchange, get_user_exchange_history,
    get_tankas_by_category, get_popular_tankas, get_category_stats,
    get_all_categories, get_all_tankas_with_categories, get_user_exchange_stats
)
import uuid
import google.generativeai as genai

import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')  # セッション用

# Google Gemini API設定
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

@app.before_request
def ensure_session():
    """セッションIDを確保"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/')
def home():
    """ホーム画面"""
    pool_count = get_pool_count()
    return render_template('home.html', pool_count=pool_count)

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
    4. 交換履歴を記録（Foreign Key使用）
    5. 取得した短歌をレスポンスとして返す
    """
    # セッションIDからユーザーを取得/作成
    session_id = session.get('session_id')
    user_id = get_or_create_user(session_id)
    
    # 5行の入力を結合
    lines = []
    for i in range(1, 6):
        line = request.form.get(f'line{i}', '').strip()
        lines.append(line)
    
    user_tanka = '\n'.join(lines)
    
    # 入力チェック
    if not any(lines):
        return render_template('submit.html', error='短歌を入力してください')
    
    # --- RAG強化: ベクトル生成 ---
    user_embedding = None
    try:
        embed_res = genai.embed_content(
            model="models/text-embedding-004",
            content=user_tanka,
            task_type="retrieval_document"
        )
        user_embedding = embed_res['embedding']
    except Exception as e:
        print(f"Embedding Generation Error: {e}")
        # エラーでも続行（ベクトルなしで登録）

    # 交換処理
    received = get_random_tanka(exclude_user_id=user_id)
    
    if received is None:
        return render_template('submit.html', error='交換できる短歌がありません')
    
    received_tanka_id, received_tanka_content = received
    
    # ユーザーの短歌を登録（ベクトル付き）
    given_tanka_id = insert_tanka(user_tanka, user_id, embedding=user_embedding)
    
    # 交換履歴を記録
    record_exchange(
        user_id=user_id,
        given_tanka_id=given_tanka_id,
        given_content=user_tanka,
        received_tanka_id=received_tanka_id,
        received_content=received_tanka_content
    )
    
    # 取得した短歌を削除
    delete_tanka(received_tanka_id)
    
    return render_template('result.html', received_tanka=received_tanka_content)

@app.route('/history')
def history():
    """受信履歴画面（データベースから取得）"""
    session_id = session.get('session_id')
    user_id = get_or_create_user(session_id)
    history = get_user_exchange_history(user_id, limit=50)
    return render_template('history.html', history=history)

@app.route('/stats')
def stats():
    """
    統計画面
    JOIN, SubQueryを使用した高度な統計機能
    """
    # 人気ランキング（SubQuery使用）
    popular_tankas = get_popular_tankas(limit=10)
    
    # カテゴリ別統計（SubQuery使用）
    category_stats = get_category_stats()
    
    # 全短歌一覧（JOIN使用）
    all_tankas = get_all_tankas_with_categories()
    
    return render_template('stats.html', 
                         popular_tankas=popular_tankas,
                         category_stats=category_stats,
                         all_tankas=all_tankas)

@app.route('/category/<category_name>')
def category(category_name):
    """
    カテゴリ別短歌一覧
    JOIN使用: tanka_pool JOIN tanka_categories JOIN categories
    """
    tankas = get_tankas_by_category(category_name)
    categories = get_all_categories()
    
    return render_template('category.html', 
                         category_name=category_name,
                         tankas=tankas,
                         categories=categories)

@app.route('/user/stats')
def user_stats():
    """
    ユーザー統計画面
    Foreign Keyを使用した履歴取得
    """
    session_id = session.get('session_id')
    user_id = get_or_create_user(session_id)
    
    # ユーザー統計（JOIN使用）
    stats = get_user_exchange_stats(user_id)
    
    # 交換履歴（Foreign Key使用）
    history = get_user_exchange_history(user_id, limit=20)
    
    return render_template('user_stats.html', stats=stats, history=history)

@app.route('/api/pool_count')
def api_pool_count():
    """プール内の短歌数を返すAPI（デバッグ用）"""
    count = get_pool_count()
    return jsonify({'count': count})

# ==================== AI 歌人（Gemini Powered） ====================

@app.route('/ai-advisor')
def ai_advisor():
    """AI歌人チャット画面"""
    pool_count = get_pool_count()
    return render_template('ai_advisor.html', pool_count=pool_count)

@app.route('/api/ai-consult', methods=['POST'])
def ai_consult():
    """
    AI相談API（実稼働プロトタイプ）
    Gemini API + DB連携
    """
    data = request.json
    user_message = data.get('message', '')
    
    # セッションからユーザーIDを取得（除外用）
    session_id = session.get('session_id')
    user_id = get_or_create_user(session_id) if session_id else None

    try:
        # 1. ユーザーのメッセージをベクトル化 (Embedding)
        embed_result = genai.embed_content(
            model="models/text-embedding-004",
            content=user_message,
            task_type="retrieval_query"
        )
        user_embedding = embed_result['embedding']

        # 2. DBからベクトル探索（セマンティック検索）で「参考短歌」を選定
        from .models import search_tanka_semantically
        ref_tanka_data = search_tanka_semantically(user_embedding, exclude_user_id=user_id)
        
        if ref_tanka_data:
            tanka_content = ref_tanka_data[1]
        else:
            tanka_content = "春過ぎて\n夏来にけらし\n白妙の\n衣ほすてふ\n天の香具山" 

        # 3. Geminiへのプロンプト作成
        prompt = f"""
        あなたは「AI歌人」です。短歌のデータベースを持つ相談役として、ユーザーの悩みに答え、参考となる短歌を紹介してください。

        【ユーザーの入力】: 「{user_message}」

        【データベースからの参考短歌（ベクトル探索による抽出）】:
        {tanka_content}

        【指示】:
        1. ユーザーの気持ちに共感してください。
        2. 参考短歌を紹介し（引用部分はHTMLタグ <div class='ref-tanka'> で囲み、改行は <br> にする）、それがどうユーザーの心情と関わるか解説してください。
        3. 全体で150文字程度で、優しく文学的な言葉遣いでまとめてください。
        """
        
        # 3. Gemini API呼び出し
        # 無料枠で高速な Flash モデルを使用
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        ai_text = response.text
        
        return jsonify({'response': ai_text})

    except Exception as e:
        import traceback
        print(f"AI Error: {e}")
        traceback.print_exc() # 詳細なエラーログを出力
        # エラー時のフォールバック
        return jsonify({'response': "申し訳ありません。現在AI歌人は瞑想中（API制限またはエラー）のようです。\n\n<div class='ref-tanka'>春過ぎて<br>夏来にけらし<br>白妙の<br>衣ほすてふ<br>天の香具山</div>\n\n代わりにこちらの歌をお届けします。また後でお話ししましょう。"})

def setup_docker_environment():
    """Dockerコンテナの起動状態を確認し、必要に応じて起動"""
    import subprocess
    import sys
    import os
    
    print("[*] Docker環境を確認中...")
    
    # 1. Dockerがインストールされているか確認
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("\n[!] Dockerがインストールされていません")
            print("   Docker Desktopをインストールしてください: https://www.docker.com/products/docker-desktop")
            sys.exit(1)
        print(f"[v] Docker検出: {result.stdout.strip()}")
    except subprocess.TimeoutExpired:
        print("\n[x] Dockerコマンドがタイムアウトしました")
        print("   Docker Desktopが起動しているか確認してください")
        sys.exit(1)
    except FileNotFoundError:
        print("\n[!] Dockerがインストールされていません")
        print("   Docker Desktopをインストールしてください: https://www.docker.com/products/docker-desktop")
        sys.exit(1)
    
    # 2. Docker Desktopが起動しているか確認（docker infoで確認）
    try:
        print("[*] Docker Desktopの起動状態を確認中...")
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            print("\n[x] Docker Desktopが起動していません")
            print("   Docker Desktopを起動してから、再度実行してください")
            print(f"   エラー詳細: {result.stderr}")
            sys.exit(1)
        print("[v] Docker Desktopは起動しています")
    except subprocess.TimeoutExpired:
        print("\n[x] Docker Desktopの確認がタイムアウトしました")
        print("   Docker Desktopを再起動してから、再度実行してください")
        sys.exit(1)
    
    # 3. docker-composeコマンドの確認
    try:
        # docker compose (V2) または docker-compose (V1) を確認
        result_v2 = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, timeout=10)
        if result_v2.returncode == 0:
            compose_cmd = ['docker', 'compose']
            print(f"[v] Docker Compose検出: {result_v2.stdout.strip()}")
        else:
            result_v1 = subprocess.run(['docker-compose', '--version'], 
                                      capture_output=True, text=True, timeout=10)
            if result_v1.returncode == 0:
                compose_cmd = ['docker-compose']
                print(f"[v] Docker Compose検出: {result_v1.stdout.strip()}")
            else:
                print("\n[x] docker-composeコマンドが見つかりません")
                sys.exit(1)
    except subprocess.TimeoutExpired:
        print("\n[x] docker-composeコマンドの確認がタイムアウトしました")
        sys.exit(1)
    except FileNotFoundError:
        print("\n[x] docker-composeコマンドが見つかりません")
        sys.exit(1)
    
    # 4. tanka_postgresコンテナが起動しているか確認
    try:
        print("[*] PostgreSQLコンテナの状態を確認中...")
        result = subprocess.run(['docker', 'ps', '--filter', 'name=tanka_postgres', '--format', '{{.Names}}'],
                              capture_output=True, text=True, timeout=15)
        
        if 'tanka_postgres' not in result.stdout:
            print("[*] PostgreSQLコンテナを起動中...")
            # docker-compose up -d を実行
            result = subprocess.run(compose_cmd + ['up', '-d'],
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print("[v] PostgreSQLコンテナを起動しました")
                if result.stdout:
                    print(f"   {result.stdout.strip()}")
            else:
                print(f"\n[x] コンテナ起動エラー:")
                print(f"   {result.stderr}")
                sys.exit(1)
        else:
            print("[v] PostgreSQLコンテナは既に起動しています")
    except subprocess.TimeoutExpired:
        print("\n[x] Dockerコンテナの起動がタイムアウトしました")
        print("   以下を確認してください:")
        print("   1. Docker Desktopが正常に動作しているか")
        print("   2. システムリソース（CPU/メモリ）に余裕があるか")
        print("   3. docker-compose.ymlファイルが存在するか")
        sys.exit(1)
    except Exception as e:
        print(f"\n[x] Docker環境のセットアップエラー: {e}")
        sys.exit(1)


def wait_for_database(max_retries=30, retry_interval=1):
    """データベース接続を確認し、接続できるまで待機"""
    import time
    from .config import get_db_connection
    
    print("[*] データベース接続を確認中...")
    
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            conn.close()
            print("[v] データベースに接続しました")
            return True
        except Exception as e:
            if i == 0:
                print(f"   データベース起動待機中... (最大{max_retries}秒)")
            time.sleep(retry_interval)
    
    print(f"[x] データベースに接続できませんでした（{max_retries}秒経過）")
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
    print("[*] データベースを初期化中...")
    from init_db import init_database
    init_database()
    
    print("\n[!] アプリケーションを起動します")
    print("   ブラウザで http://localhost:5000 にアクセスしてください\n")
    
    # 4. Flaskアプリ起動
    app.run(debug=True, host='0.0.0.0', port=5000)
