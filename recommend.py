from openai import OpenAI
import os
import json

ai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=ai_key)

def get_stock_decision(prompt: str) -> tuple[bool, str]:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},          # wichtig!
        messages=[
            {"role": "system",
             "content": (
                 "Du bist ein erfahrener Börsenanalyst. "
                 "Antworte ausschließlich als JSON: "
                 '{"decision":"JA|NEIN","reason":"Knappe Begründung"}'
             )},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=60
    )

    data = json.loads(response.choices[0].message.content)
    return data["decision"].lower() == "ja", data["reason"]

