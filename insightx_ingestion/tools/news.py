import newspaper
import httpx
from urllib.parse import urlparse

async def fetch_article(url: str) -> dict:
    """Extract article body using newspaper3k with fallback to raw fetch."""
    try:
        # newspaper3k has parsing issues occasionally, need to use article correctly
        article = newspaper.Article(url)
        article.download()
        article.parse()
        
        return {
            "title": article.title or "Unknown Title",
            "text": article.text or "No content extracted.",
            "url": url
        }
    except Exception as e:
        print(f"Newspaper3k failed for {url}: {e}")
        # Fallback raw fetch attempt
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=10.0)
                return {
                    "title": urlparse(url).netloc,
                    "text": res.text[:2000], # return partial raw HTML as last resort
                    "url": url
                }
        except Exception as fallback_e:
            return {
                "title": "Error",
                "text": f"Failed to fetch content entirely: {fallback_e}",
                "url": url
            }
