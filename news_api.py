"""
api/news_api.py — Latest news headlines using NewsAPI
Free tier: 100 requests/day — plenty for daily use
Get key at: https://newsapi.org
"""

import requests
from utils.logger import get_logger
from config import NEWS_API_KEY

logger = get_logger(__name__)

BASE_URL = "https://newsapi.org/v2/top-headlines"


class NewsAPI:

    def get_top_headlines(self, country: str = "in", count: int = 5) -> str:
        """
        Fetch top headlines and return as a spoken summary.
        country: "in" for India, "us" for US, "gb" for UK
        """
        if not NEWS_API_KEY:
            return "News API key is missing. Please add it to your .env file."

        try:
            params = {
                "country":  country,
                "pageSize": count,
                "apiKey":   NEWS_API_KEY
            }
            response = requests.get(BASE_URL, params=params, timeout=5)
            data = response.json()

            if response.status_code != 200 or data.get("status") != "ok":
                logger.warning(f"News API error: {data.get('message')}")
                return "I couldn't fetch the news right now. Please try again later."

            articles = data.get("articles", [])
            if not articles:
                return "No news headlines found right now."

            return self._format_headlines(articles)

        except requests.Timeout:
            return "News request timed out. Please check your internet."
        except Exception as e:
            logger.error(f"News fetch error: {e}")
            return "Something went wrong while fetching the news."

    def _format_headlines(self, articles: list) -> str:
        """Format articles into a natural spoken news bulletin."""
        intro = "Here are today's top headlines. "
        headlines = []

        for i, article in enumerate(articles, 1):
            title  = article.get("title", "")
            source = article.get("source", {}).get("name", "")

            # Clean up title — remove source name appended at end
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]

            if title:
                headlines.append(f"Headline {i}: {title}.")

        if not headlines:
            return "No readable headlines found right now."

        return intro + " ".join(headlines)

    def get_tech_news(self) -> str:
        """Fetch technology news specifically."""
        if not NEWS_API_KEY:
            return "News API key is missing."
        try:
            params = {
                "category": "technology",
                "country":  "in",
                "pageSize": 3,
                "apiKey":   NEWS_API_KEY
            }
            response = requests.get(BASE_URL, params=params, timeout=5)
            data = response.json()
            articles = data.get("articles", [])
            return self._format_headlines(articles) if articles else "No tech news found."
        except Exception as e:
            logger.error(f"Tech news error: {e}")
            return "Couldn't fetch tech news."

    def get_sports_news(self) -> str:
        """Fetch sports news."""
        if not NEWS_API_KEY:
            return "News API key is missing."
        try:
            params = {
                "category": "sports",
                "country":  "in",
                "pageSize": 3,
                "apiKey":   NEWS_API_KEY
            }
            response = requests.get(BASE_URL, params=params, timeout=5)
            data = response.json()
            articles = data.get("articles", [])
            return self._format_headlines(articles) if articles else "No sports news found."
        except Exception as e:
            return "Couldn't fetch sports news."


# ── Singleton ─────────────────────────────────────────────
_api = None

def get_news(country: str = "in") -> str:
    global _api
    if _api is None:
        _api = NewsAPI()
    return _api.get_top_headlines(country)


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    print(get_news())