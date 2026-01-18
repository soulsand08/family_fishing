
import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_ai():
    load_dotenv()
    api_key = os.getenv("GENAI_API_KEY")
    if not api_key:
        print("Error: GENAI_API_KEY not found in .env")
        return

    genai.configure(api_key=api_key)
    
    try:
        print("Testing Embedding API...")
        embed_result = genai.embed_content(
            model="models/text-embedding-004",
            content="テストメッセージ",
            task_type="retrieval_query"
        )
        print("Embedding Success!")

        print("Testing Generative Model...")
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content("こんにちは、一言挨拶してください。")
        print(f"Generation Success: {response.text}")

    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    test_ai()
