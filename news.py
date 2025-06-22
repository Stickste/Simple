import requests
from datetime import datetime, timedelta
from keys import News_key
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

API_KEY = News_key  # <-- deinen Key einfügen
BASE_URL = "https://newsapi.org/v2/everything"

analyzer = SentimentIntensityAnalyzer()

def get_news_articles(ticker: str):
    def fetch_news(query, from_date, to_date, page_size=5):
        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "sortBy": "popularity",  # Changed to popularity
            "language": "en",
            "pageSize": page_size,
            "apiKey": API_KEY,
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            return []

    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    last_month = today - timedelta(days=30)

    # Fetch articles
    last_day_articles = fetch_news(ticker, yesterday.date(), today.date(), page_size=2)
    monthly_article = fetch_news(ticker, last_month.date(), today.date(), page_size=1)

    combined = last_day_articles + monthly_article

    result = []
    for article in combined:
        text = f"{article.get('title', '')} {article.get('description', '')}"
        score = analyzer.polarity_scores(text)["compound"]
        label = (
            "positive" if score > 0.05 else
            "negative" if score < -0.05 else
            "neutral"
        )

        result.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("name"),
            "publishedAt": article.get("publishedAt", "")[:10],
            "ticker": ticker.upper(),
            "sentiment_score": round(score, 3),
            "sentiment_label": label
        })

    return result
