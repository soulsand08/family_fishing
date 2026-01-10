# SQL要素強化: 実装完了レポート

Foreign Key、JOIN、SubQueryを含む本格的なSQL機能の実装が完了しました。

## 実装されたSQL要素

### 1. Foreign Key制約

以下のForeign Key制約を実装しました:

| テーブル | カラム | 参照先 | ON DELETE |
|---------|--------|--------|-----------|
| `tanka_pool` | `user_id` | `users(user_id)` | SET NULL |
| `exchange_history` | `user_id` | `users(user_id)` | CASCADE |
| `tanka_categories` | `tanka_id` | `tanka_pool(id)` | CASCADE |
| `tanka_categories` | `category_id` | `categories(category_id)` | CASCADE |

**参照整合性の保証:**
- ユーザーが削除されると、関連する交換履歴も自動削除
- 短歌が削除されると、カテゴリとの関連も自動削除

---

### 2. JOIN操作

#### 3テーブルのINNER JOIN
```python
# models.py: get_tankas_by_category()
SELECT tp.id, tp.content, c.name
FROM tanka_pool tp
INNER JOIN tanka_categories tc ON tp.id = tc.tanka_id
INNER JOIN categories c ON tc.category_id = c.category_id
WHERE c.name = %s
```

#### LEFT JOIN + GROUP BY + STRING_AGG
```python
# models.py: get_all_tankas_with_categories()
SELECT 
    tp.id, tp.content,
    STRING_AGG(c.name, ', ') as categories,
    tp.exchange_count
FROM tanka_pool tp
LEFT JOIN tanka_categories tc ON tp.id = tc.tanka_id
LEFT JOIN categories c ON tc.category_id = c.category_id
GROUP BY tp.id, tp.content, tp.exchange_count
```

---

### 3. SubQuery

#### 相関サブクエリ（人気ランキング）
```python
# models.py: get_popular_tankas()
SELECT 
    tp.id, tp.content,
    COALESCE(
        (SELECT COUNT(*) 
         FROM exchange_history eh 
         WHERE eh.received_tanka_id = tp.id),
        0
    ) as exchange_count
FROM tanka_pool tp
ORDER BY exchange_count DESC
```

#### スカラーサブクエリ（カテゴリ統計）
```python
# models.py: get_category_stats()
SELECT 
    c.name,
    (SELECT COUNT(*) 
     FROM tanka_categories tc 
     WHERE tc.category_id = c.category_id) as tanka_count
FROM categories c
```

---

## 新機能

### 📊 統計画面 (`/stats`)
- **人気ランキングTOP10** - SubQueryで交換回数を集計
- **カテゴリ別統計** - SubQueryで各カテゴリの短歌数を表示
- **全短歌一覧** - JOINでカテゴリ情報付きで表示

### 📚 カテゴリ検索 (`/category/<name>`)
- **3テーブルのJOIN** - tanka_pool ⋈ tanka_categories ⋈ categories
- カテゴリ別に短歌を絞り込み表示

### 👤 ユーザー統計 (`/user/stats`)
- **Foreign Key活用** - users ⋈ exchange_history
- ユーザーごとの交換統計と履歴を表示

---

## データベーススキーマ

```
users (ユーザー)
├── user_id (PK)
├── session_id (UNIQUE)
└── created_at

categories (カテゴリ)
├── category_id (PK)
├── name (UNIQUE)
└── description

tanka_pool (短歌プール)
├── id (PK)
├── content
├── user_id (FK → users)
├── exchange_count
└── created_at

exchange_history (交換履歴)
├── exchange_id (PK)
├── user_id (FK → users)
├── given_tanka_id
├── received_tanka_id
└── exchanged_at

tanka_categories (短歌-カテゴリ関連)
├── tanka_id (FK → tanka_pool)
└── category_id (FK → categories)
    PRIMARY KEY (tanka_id, category_id)
```

---

## 動作確認方法

1. **データベース初期化**
   ```bash
   python init_db.py
   ```

2. **アプリケーション起動**
   ```bash
   python desktop_app.py
   ```

3. **確認項目**
   - ホーム画面から「統計を見る」をクリック
   - カテゴリ別統計を確認（SubQuery動作確認）
   - 人気ランキングを確認（SubQuery動作確認）
   - カテゴリ名をクリック（JOIN動作確認）
   - 短歌を交換（Foreign Key制約確認）
   - 「マイ統計」で履歴確認（Foreign Key活用確認）

---

## 技術的ハイライト

✅ **Foreign Key制約** - 4つの参照整合性制約を実装  
✅ **JOIN操作** - 2テーブル、3テーブルのJOINを実装  
✅ **SubQuery** - 相関サブクエリ、スカラーサブクエリを実装  
✅ **集約関数** - COUNT, STRING_AGG, COALESCE  
✅ **GROUP BY / HAVING** - カテゴリ別集計  
✅ **CASCADE削除** - 親レコード削除時の自動処理  

これで課題要件（Foreign Key, JOIN, SubQuery）を完全に満たしています！
