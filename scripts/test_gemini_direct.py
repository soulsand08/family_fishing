import os
import google.generativeai as genai
import traceback
from dotenv import load_dotenv

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

def test_ai_call():
    user_message = "テストです。最近疲れています。"
    tanka_content = "古池や\n蛙飛び込む\n水の音"
    
    prompt = f"""
    あなたは「AI歌人」です。短歌のデータベースを持つ相談役として、ユーザーの悩みに答え、参考となる短歌を紹介してください。

    【ユーザーの入力】: 「{user_message}」

    【データベースからの参考短歌】:
    {tanka_content}

    【指示】:
    1. ユーザーの気持ちに共感してください。
    2. 参考短歌を紹介し（引用部分はHTMLタグ `<div class='ref-tanka'>` で囲み、改行は `<br>` にする）、それがどうユーザーの心情と関わるか解説してください。
    3. 全体で150文字程度で、優しく文学的な言葉遣いでまとめてください。
    """
    
    try:
        print(f"Calling Gemini with model: gemini-flash-latest")
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        print("Success!")
        print(f"Response: {response.text}")
    except Exception as e:
        print("!!! Error Detcted !!!")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_call()
