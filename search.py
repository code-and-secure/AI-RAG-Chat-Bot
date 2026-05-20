import requests
from bs4 import BeautifulSoup
from googlesearch import search
from duckduckgo_search import DDGS

def fetch_page_text(url: str, max_chars: int = 4000) -> str:
    """Fetch and clean visible text from a webpage for LLM context."""
    try:
        response = requests.get(
            url,
            timeout=8,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = " ".join(soup.get_text(separator=" ").split())
        return text[:max_chars]
    except Exception:
        return ""

def google_search_context(user_query: str, num_results: int = 3):
    """Return concatenated web context and source URLs from Google results."""
    urls = []
    context_parts = []

    try:
        for url in search(user_query, num_results=num_results):
            urls.append(url)
            page_text = fetch_page_text(url)
            if page_text:
                context_parts.append(f"Source: {url}\nContent: {page_text}")
    except Exception:
        pass

    # Fallback provider when Google blocks automated requests.
    if not context_parts:
        try:
            with DDGS() as ddgs:
                results = ddgs.text(user_query, max_results=num_results)
                for item in results:
                    url = item.get("href")
                    if not url:
                        continue
                    urls.append(url)
                    page_text = fetch_page_text(url)
                    if page_text:
                        context_parts.append(f"Source: {url}\nContent: {page_text}")
        except Exception:
            return "", []

    return "\n\n".join(context_parts), urls
