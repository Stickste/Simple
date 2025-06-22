from openai import OpenAI
import os
from keys import ai_key

client = OpenAI(api_key=ai_key)

def get_recommended_stocks():
    # Schritt 1: GPT generiert Empfehlungen
    prompt1 = (
        "Basierend auf allen Informationen, die dir bereitstehen, "
        "welche 3 Aktien soll ich am Montag kaufen und am Dienstag wieder verkaufen, "
        "um den größtmöglichen Gewinn zu erzielen? Begründe deine Auswahl."
    )

    try:
        response1 = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein Börsen- und Aktienexperte."},
                {"role": "user", "content": prompt1}
            ],
            temperature=0.7,
            max_tokens=500
        )

        antwort = response1.choices[0].message.content
        print("GPT-Antwort:", antwort)

        # Schritt 2: GPT extrahiert nur die Ticker
        prompt2 = (
            f"Hier ist eine Antwort mit Aktienempfehlungen:\n\n\"{antwort}\"\n\n"
            "Gib mir bitte nur die Ticker-Symbole zurück (z. B. AAPL, TSLA, NVDA), "
            "als kommagetrennte Liste – keine Erklärungen, nur die Symbole."
        )

        response2 = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extrahiere nur die Ticker-Symbole."},
                {"role": "user", "content": prompt2}
            ],
            temperature=0.2,
            max_tokens=20
        )

        tickers_raw = response2.choices[0].message.content.strip()
        tickers = [t.strip().upper() for t in tickers_raw.split(",") if t]

        return tickers[:3]

    except Exception as e:
        print("Fehler bei GPT-Anfrage:", e)
        return []

# Zum Testen
if __name__ == "__main__":
    print(get_recommended_stocks())