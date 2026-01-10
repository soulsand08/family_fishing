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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
