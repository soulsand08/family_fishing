"""
update_embeddings.py - 既存短歌のベクトル埋め込みを生成・更新するスクリプト
"""
import sys
import os
import google.generativeai as genai
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_db_connection
from app.models import update_tanka_embedding, get_tankas_without_embeddings

def main():
    load_dotenv()
    api_key = os.getenv("GENAI_API_KEY")
    if not api_key:
        print("[x] GOOGLE_API_KEY が設定されていません")
        return

    genai.configure(api_key=api_key)
    
    print("[*] ベクトル未生成の短歌を取得中...")
    tankas = get_tankas_without_embeddings()
    
    if not tankas:
        print("[v] すべての短歌にベクトルが付与されています")
        return
    
    print(f"[*] {len(tankas)} 件の短歌のベクトルを生成します")
    
    for tanka_id, content in tankas:
        try:
            print(f"  - ID {tanka_id} のベクトルを生成中...")
            # text-embedding-004 を使用 (768次元)
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=content,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
            update_tanka_embedding(tanka_id, embedding)
        except Exception as e:
            print(f"  [!] ID {tanka_id} でエラー: {e}")
            
    print("\n[v] すべての更新が完了しました")

if __name__ == "__main__":
    main()
