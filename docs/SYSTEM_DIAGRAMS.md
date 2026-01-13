# システム設計図面集 (Mermaid)

プレゼンテーションやレポートにそのまま貼り付けて使用できる、最新のシステム構成図、ER 図、およびシーケンス図です。

---

## 1. システム構成図 (System Architecture)

Web 3 層構造に基づいた物理的なコンポーネントの配置図です。

```mermaid
graph TD
    subgraph "Presentation Tier (Client)"
        A["ブラウザ / PyWebView Window"]
    end

    subgraph "Application Tier (Server)"
        B["Waitress WSGI Server"]
        C["Flask Framework"]
        D["Business Logic / app.main.py"]
    end

    subgraph "Data Tier (Infrastructure)"
        E["PostgreSQL 15 / Docker"]
        F["Database Volume"]
    end

    A <-->|HTTP Request/Response| B
    B --- C
    C --- D
    D <-->|SQL / psycopg2| E
    E --- F
```

---

## 2. 実体関連図 (ER Diagram)

データベースのテーブル構造と、外部キーによるリレーションシップを示します。

```mermaid
erDiagram
    users ||--o{ tanka_pool : "posted by"
    users ||--o{ exchange_history : "exchanged by"
    tanka_pool ||--o{ tanka_categories : "categorized by"
    categories ||--o{ tanka_categories : "belongs to"
    tanka_pool ||--o{ exchange_history : "referenced as given/received"

    users {
        int user_id PK
        string session_id UK
        string username
        timestamp created_at
    }

    tanka_pool {
        int id PK
        text content
        int user_id FK
        int exchange_count
        timestamp created_at
    }

    categories {
        int category_id PK
        string name UK
        text description
    }

    tanka_categories {
        int tanka_id FK, PK
        int category_id FK, PK
    }

    exchange_history {
        int exchange_id PK
        int user_id FK
        int given_tanka_id FK
        int received_tanka_id FK
        timestamp exchanged_at
    }
```

---

## 3. シーケンス図 (Sequence Diagram)

「短歌を投稿して交換する」という本アプリのメインフローの流れを示します。

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant Front as フロントエンド (JS)
    participant Server as アプリサーバー (Flask/Waitress)
    participant DB as データ層 (PostgreSQL)

    User->>Front: 短歌を入力・送信
    Front->>Server: POST /exchange (短歌データ)

    rect rgb(240, 240, 240)
        Note over Server, DB: トランザクション開始
        Server->>DB: ランダムな短歌を1件取得
        DB-->>Server: 短歌データ (received_tanka)
        Server->>DB: 取得した短歌を削除 (DELETE)
        Server->>DB: ユーザーの短歌を保存 (INSERT)
        Server->>DB: 交換履歴を記録 (INSERT)
        Server->>DB: 交換回数を加算 (UPDATE)
        Note over Server, DB: トランザクション終了
    end

    Server-->>Front: 交換後の短歌データを返却
    Front->>User: 画面に新しい短歌を表示
    Front->>Front: LocalStorage に履歴を保存
```

---

## 4. 起動・初期化シーケンス

アプリ起動時の自動セットアップの流れです。

```mermaid
sequenceDiagram
    participant App as "desktop_app.py"
    participant Main as "app.main / setup"
    participant Docker as "Docker Engine"
    participant DB as "PostgreSQL"

    App->>Main: setup_docker_environment()
    Main->>Docker: docker-compose up -d
    Docker-->>Main: コンテナ起動完了
    Main->>Main: wait_for_database()
    loop 接続試行
        Main->>DB: 接続確認 (psycopg2)
    end
    DB-->>Main: 接続成功
    Main->>Main: init_database()
    Main-->>App: セットアップ完了
    App->>App: "Waitress + WebView 起動"
```
