# 匿名短歌交換アプリ プレゼンテーション資料

## 1. プロジェクト概要

**「一期一会の言葉を交わす」**

- **コンセプト**: 匿名で短歌を投稿し、誰かの詠んだ短歌とランダムに交換する。
- **特徴**: 受信した短歌は DB から削除され、自分の短歌が新しく保存される。
- **こだわり**: データの流動性と、Web 3 層構造に基づいた堅牢な設計。

---

## 2. システム構成 (Web 3 層構造)

本システムは、保守性と拡張性を考慮した本格的な 3 層構造を採用しています。

```mermaid
graph TD
    subgraph "プレゼンテーション層 (Presentation Tier)"
        A["ブラウザ / PyWebView Window"]
    end

    subgraph "アプリケーション層 (Application Tier)"
        B["Waitress WSGI Server"]
        C["Flask Framework"]
        D["Business Logic"]
    end

    subgraph "データ層 (Data Tier)"
        E["PostgreSQL 15 / Docker"]
        F["Database Volume"]
    end

    A <-->|HTTP Request/Response| B
    B --- C
    C --- D
    D <-->|SQL / psycopg2| E
    E --- F
```

- **Presentation**: ユーザーとの接点（HTML/CSS/JS/PyWebView）
- **Application**: 業務ロジックの管理（Waitress/Flask）
- **Data**: 情報の永続化と整合性担保（PostgreSQL/Docker）

---

## 3. データベース設計 (ER 図)

データの整合性を保つため、外部キー制約と正規化（第 3 回正規化レベル）を徹底しています。

```mermaid
erDiagram
    users ||--o{ tanka_pool : "posted by"
    users ||--o{ exchange_history : "exchanged by"
    tanka_pool ||--o{ tanka_categories : "categorized by"
    categories ||--o{ tanka_categories : "belongs to"
    tanka_pool ||--o{ exchange_history : "referenced"

    users {
        int user_id PK
        string session_id UK "重複不可"
        string username
        timestamp created_at
    }

    tanka_pool {
        int id PK
        text content "短歌本文"
        int user_id FK
        int exchange_count
        timestamp created_at
    }

    categories {
        int category_id PK
        string name UK "春/夏/秋/冬..."
        text description
    }

    exchange_history {
        int exchange_id PK
        int user_id FK
        int given_tanka_id FK
        int received_tanka_id FK
        timestamp exchanged_at
    }
```

- **一意性制約(UK)**: 重複登録の防止
- **外部キー(FK)**: データの不整合（ゴミデータの発生）を DB レベルで防止

---

## 4. 主要な処理フロー (シーケンス図)

最も重要な「短歌交換」の裏側では、アトミックなトランザクション処理が行われています。

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant Front as UI (JS)
    participant Server as Flask/Waitress
    participant DB as PostgreSQL

    User->>Front: 短歌を入力・送信
    Front->>Server: POST /exchange

    rect rgb(240, 240, 240)
        Note over Server, DB: トランザクション (整合性保証)
        Server->>DB: 他者の短歌をLEMIT 1でランダム抽出
        DB-->>Server: 受信データ
        Server->>DB: 抽出した短歌をDELETE
        Server->>DB: 送信した短歌をINSERT
        Server->>DB: 履歴をRECORD
    end

    Server-->>Front: JSON (受信データ)
    Front->>User: 画面に表示 & LocalStorage保存
```

---

## 5. 技術的な挑戦と解決策

1. **本番環境への対応**: 開発用サーバーではなく、**Waitress (WSGI)** を導入し、並列処理と安定性を向上。
2. **起動の自動化**: `docker-compose` の自動制御を実装し、ユーザーがコマンド一つでインフラまで起動できる環境を実現。
3. **障害への強さ**: データベースの構成不整合を自動検知して修正する「マイグレーション機能」を実装。

---

## 6. まとめ

本プロジェクトを通じて、単なるプログラミングだけでなく、エンジニアリングにおける**「3 層構造の重要性」**、**「データベースの整合性管理」**、そして**「本番環境を見据えたインフラ設計」**を深く学ぶことができました。

以上で発表を終わります。ご清聴ありがとうございました。
