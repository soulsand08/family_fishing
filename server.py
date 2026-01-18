"""
server.py - プロダクション用サーバー起動スクリプト
Waitressを使用してWebアプリケーションサーバーを起動
"""
import sys
from waitress import serve
from app import app, setup_docker_environment, wait_for_database

def main():
    """メイン処理"""
    print("=== 匿名短歌交換 アプリケーションサーバー起動 (Waitress) ===\n")
    
    # 1. Docker環境のセットアップ
    setup_docker_environment()
    
    # 2. データベース接続確認
    if not wait_for_database():
        print("\n[x] データベースに接続できませんでした")
        print("  アプリケーションを終了します")
        sys.exit(1)
    
    # 3. データベース初期化（初回のみ）
    print("[*] データベースを初期化中...")
    from scripts.init_db import init_database
    init_database()
    
    print("\n[*] サーバーを http://127.0.0.1:5000 で起動します...")
    print("  (停止するには Ctrl+C を入力してください)\n")
    
    # 4. Waitressサーバーを起動
    serve(app, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
