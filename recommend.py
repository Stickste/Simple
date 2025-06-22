from openai import OpenAI
from keys import ai_key

client = OpenAI(api_key=ai_key)

def should_buy_stock(prompt: str) -> bool:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein erfahrener Börsenanalyst. Antworte immer mit JA oder NEIN."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=10
        )

        content = response.choices[0].message.content.strip().lower()
        return "ja" in content or "yes" in content

    except Exception as e:
        print("❌ Fehler bei should_buy_stock:", e)
        return False

