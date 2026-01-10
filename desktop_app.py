"""
desktop_app.py - デスクトップアプリケーション起動スクリプト
PyWebViewを使用してFlaskアプリをデスクトップアプリとして起動
"""
import webview
import threading
import time
import sys
from app import app, setup_docker_environment, wait_for_database

def start_flask():
    """Flaskアプリをバックグラウンドで起動"""
    # デバッグモードをオフにして起動（デスクトップアプリでは不要）
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def main():
    """メイン処理"""
    print("=== 匿名短歌交換 デスクトップアプリ起動 ===\n")
    
    # 1. Docker環境のセットアップ
    setup_docker_environment()
    
    # 2. データベース接続確認
    if not wait_for_database():
        print("\n✗ データベースに接続できませんでした")
        print("  アプリケーションを終了します")
        sys.exit(1)
    
    # 3. データベース初期化（初回のみ）
    print("📊 データベースを初期化中...")
    from init_db import init_database
    init_database()
    
    print("\n✨ デスクトップアプリケーションを起動します\n")
    
    # 4. Flaskを別スレッドで起動
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Flaskが起動するまで少し待機
    time.sleep(2)
    
    # 5. デスクトップウィンドウを作成
    webview.create_window(
        title='匿名短歌交換',
        url='http://127.0.0.1:5000',
        width=900,
        height=700,
        resizable=True,
        fullscreen=False,
        min_size=(600, 500)
    )
    
    # 6. ウィンドウを表示
    webview.start()
    
    print("\n👋 アプリケーションを終了しました")

if __name__ == '__main__':
    main()
