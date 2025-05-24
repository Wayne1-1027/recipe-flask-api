from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

API_URL = "https://free.v36.cm/v1/chat/completions"
API_KEY = "sk-TKz3Z8EY41ZkXwavF939421b27D54771B659Df2bA5Aa7fAb"  # ← 請替換為你自己的 key

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

@app.route('/generate-recipe', methods=['POST'])
def generate_recipe():
    data = request.get_json()
    print("✅ Received payload:", data)

    # 使用者設定
    requirements = {
        "主菜數量": data.get('dishCount'),
        "湯品數量": data.get('soupCount'),
        "主食": data.get('staple'),
        "主菜選項數": data.get('mainDishCount'),
        "額外預算": f"{data.get('extraBudget')} 元"
    }
    ingredients_list = data.get('ingredients', [])

    # 系統角色
    system_msg = {
        "role": "system",
        "content": "你是一位中式料理大廚，請依照需求輸出純 JSON 格式菜單，不加多餘解釋。"
    }

    # 使用者請求格式
    user_msg = {
        "role": "user",
        "content": f"""
請依照以下條件產出中式料理建議，格式請嚴格為 JSON（不要多餘文字）：
{{
  "dishes": [
    {{
      "title": "料理名稱",
      "ingredients": ["食材1", "食材2"],
      "seasonings": ["調味料1", "調味料2"],
      "steps": ["步驟1", "步驟2"],
      "estimated_cost": "金額"
    }}
  ]
}}

使用者需求如下：
主菜數量：{requirements['主菜數量']}
湯品數量：{requirements['湯品數量']}
主食：{requirements['主食']}
主菜選項數：{requirements['主菜選項數']}
額外預算：{requirements['額外預算']}
可使用食材：{', '.join(ingredients_list)}
"""
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [system_msg, user_msg],
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    print("📡 GPT status:", response.status_code)

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"].strip()

        # 🔧 移除 ```json 或 ``` 包裹的 markdown 格式
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        elif content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        print("📦 Cleaned GPT JSON:", content[:100], "...")

        try:
            dishes_json = json.loads(content)
            return jsonify({
                "requirements": requirements,
                "ingredients": ingredients_list,
                "dishes": dishes_json["dishes"]
            })
        except Exception as e:
            print("❌ JSON 解析錯誤:", e)
            return jsonify({"error": "GPT 回傳格式錯誤", "raw": content}), 400
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == '__main__':
    print("🚀 Flask server running on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
