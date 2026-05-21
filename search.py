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
            pass

    # Secondary API Fallback (Wikipedia) if scraping fails completely
    if not context_parts:
        try:
            headers = {"User-Agent": "DocuMind-AI-Bot/1.0 (test@example.com)"}
            wiki_search = requests.get(
                f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={user_query}&utf8=&format=json",
                headers=headers,
                timeout=5
            ).json()
            if "query" in wiki_search and wiki_search["query"]["search"]:
                for item in wiki_search["query"]["search"][:num_results]:
                    page_id = item["pageid"]
                    wiki_page = requests.get(
                        f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&pageids={page_id}&explaintext=true&format=json",
                        headers=headers,
                        timeout=5
                    ).json()
                    extract = wiki_page["query"]["pages"][str(page_id)]["extract"]
                    url = f"https://en.wikipedia.org/wiki/?curid={page_id}"
                    urls.append(url)
                    context_parts.append(f"Source: {url}\nContent: {extract[:2000]}")
        except Exception:
            return "", []

    return "\n\n".join(context_parts), urls
