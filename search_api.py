"""
api/search_api.py — General information lookups via web search
Uses DuckDuckGo Instant Answers API (free, no API key needed!)
+ Wikipedia API for factual questions.
"""

import requests
import urllib.parse
from utils.logger import get_logger

logger = get_logger(__name__)

DDG_URL  = "https://api.duckduckgo.com/"
WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"


class SearchAPI:

    # ── DuckDuckGo Instant Answer ─────────────────────────

    def search(self, query: str) -> str:
        """
        Search DuckDuckGo for an instant answer.
        Great for: definitions, quick facts, conversions, calculations.
        No API key needed — completely free.
        """
        if not query or not query.strip():
            return "What should I search for?"

        query = query.strip()
        logger.info(f"Searching DuckDuckGo: {query}")

        try:
            params = {
                "q":      query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            response = requests.get(DDG_URL, params=params, timeout=6)
            data = response.json()

            # Try to get the best answer
            answer = (
                data.get("Answer") or
                data.get("AbstractText") or
                data.get("Definition") or
                ""
            )

            if answer and len(answer.strip()) > 10:
                # Trim to a speakable length
                if len(answer) > 400:
                    answer = answer[:400].rsplit(" ", 1)[0] + "."
                logger.info(f"DuckDuckGo answer found.")
                return answer

            # No direct answer — try Wikipedia
            wiki_result = self.wikipedia(query)
            if wiki_result:
                return wiki_result

            # Nothing found — suggest Google
            return (
                f"I couldn't find a direct answer for '{query}'. "
                f"Let me open Google for you."
            )

        except requests.Timeout:
            return "Search timed out. Please check your internet connection."
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return f"I had trouble searching for that. Try asking differently."

    # ── Wikipedia ─────────────────────────────────────────

    def wikipedia(self, topic: str) -> str | None:
        """
        Fetch a summary from Wikipedia.
        Returns a 2-3 sentence spoken summary or None if not found.
        """
        topic = topic.strip().replace(" ", "_")
        logger.info(f"Wikipedia lookup: {topic}")

        try:
            url      = WIKI_URL + urllib.parse.quote(topic)
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                return None

            data    = response.json()
            extract = data.get("extract", "")

            if not extract or len(extract) < 20:
                return None

            # Take first 2 sentences
            sentences = extract.split(". ")
            summary   = ". ".join(sentences[:2]) + "."

            if len(summary) > 500:
                summary = summary[:500].rsplit(" ", 1)[0] + "."

            return summary

        except Exception as e:
            logger.debug(f"Wikipedia lookup failed: {e}")
            return None

    def search_wikipedia(self, topic: str) -> str:
        """Public method that always returns a string."""
        result = self.wikipedia(topic)
        if result:
            return result
        return f"I couldn't find a Wikipedia article about {topic}."

    # ── Calculations & Unit Conversions ───────────────────

    def calculate(self, expression: str) -> str:
        """
        Evaluate a math expression safely.
        Example: "25 * 4 + 10" → "The answer is 110."
        """
        try:
            # Only allow safe math characters
            safe = expression.replace("x", "*").replace("^", "**")
            import re
            if not re.match(r'^[\d\s\+\-\*\/\.\(\)\%\*\^]+$', safe):
                return f"I can only calculate simple math expressions."

            result = eval(safe)

            # Format result nicely
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 4)

            return f"The answer is {result}."
        except ZeroDivisionError:
            return "You can't divide by zero!"
        except Exception as e:
            logger.error(f"Calculate error: {e}")
            return f"I couldn't calculate that expression."

    # ── Dictionary ────────────────────────────────────────

    def define_word(self, word: str) -> str:
        """Get the definition of a word using DuckDuckGo."""
        return self.search(f"define {word}")

    # ── General smart search ──────────────────────────────

    def smart_search(self, query: str) -> str:
        """
        Intelligently choose between: calculate, define, or web search.
        This is the main entry point used by command_router.
        """
        q = query.lower().strip()

        # Math expression
        import re
        if re.search(r'\d+\s*[\+\-\*\/\^x]\s*\d+', q):
            return self.calculate(query)

        # Definition
        if q.startswith(("what is", "who is", "define", "meaning of", "explain")):
            result = self.wikipedia(query)
            if result:
                return result

        # General search
        return self.search(query)


# ── Singleton ─────────────────────────────────────────────
_api = None

def search(query: str) -> str:
    global _api
    if _api is None:
        _api = SearchAPI()
    return _api.smart_search(query)


def wikipedia_search(topic: str) -> str:
    global _api
    if _api is None:
        _api = SearchAPI()
    return _api.search_wikipedia(topic)


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    api = SearchAPI()
    print(api.smart_search("What is machine learning"))
    print(api.smart_search("25 * 4 + 10"))
    print(api.smart_search("define serendipity"))
    print(api.wikipedia("Elon Musk"))