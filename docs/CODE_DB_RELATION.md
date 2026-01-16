# 機能とプログラムファイルの対応表

プレゼン中に「この機能のコードはどこ？」と聞かれた際や、自分でコードを見せる時に役立つ対応表です。

---

## 1. 📂 データベースの基本構造（設計図）

すべてのテーブルの定義（CREATE TABLE）や、最初のサンプルデータについては以下のファイルにあります。

- **ファイル**: `scripts/init_db.py`
- **内容**: 5 つのテーブル（users, categories, tanka_pool, exchange_history, tanka_categories）の設計。

---

## 2. 🚀 機能別の対応ファイル

### ① 短歌を交換する

- **フロントエンド（画面）**: `app/templates/submit.html`
- **処理（ロジック）**: `app/main.py` の `exchange()` 関数
- **DB 操作（SQL）**: `app/models.py` の以下の関数
  - `get_or_create_user`: ユーザーの特定
  - `get_random_tanka`: 相手の歌を 1 件取得
  - `insert_tanka`: 自分の歌を保存
  - `record_exchange`: 交換履歴を記録
  - `delete_tanka`: 取得した歌をプールから削除

### ② 受け取った短歌を見る

- **フロントエンド（画面）**: `app/templates/history.html`
- **処理（ロジック）**: 同ファイル内の `<script>` タグ（JavaScript）
- **DB 操作**: なし（プライバシー保護と負荷軽減のため、ブラウザの **LocalStorage** で完結させています）

### ③ 統計を見る

- **フロントエンド（画面）**: `app/templates/stats.html`
- **処理（ロジック）**: `app/main.py` の `stats()` 関数
- **DB 操作（SQL）**: `app/models.py` の以下の関数
  - `get_popular_tankas`: **SubQuery** を使った人気順位
  - `get_category_stats`: **SubQuery** を使ったカテゴリごと集計
  - `get_all_tankas_with_categories`: **JOIN** を使った全短歌一覧

### ④ マイ統計

- **フロントエンド（画面）**: `app/templates/user_stats.html`
- **処理（ロジック）**: `app/main.py` の `user_stats()` 関数
- **DB 操作（SQL）**: `app/models.py` の以下の関数
  - `get_user_exchange_stats`: **JOIN** を使った個人統計
  - `get_user_exchange_history`: **Foreign Key** を使った過去 20 件の履歴

---

## 💡 先生に見せる時のポイント

「**SQL の中身を見せたい時**は、一貫して `app/models.py` を開けば、すべての高度なクエリ（JOIN, SubQuery, Transaction）が確認できます」と伝えると、プログラムの構造が整理されていることがアピールできます。
