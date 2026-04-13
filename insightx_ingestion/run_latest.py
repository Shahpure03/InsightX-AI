import asyncio
from db.supabase_client import get_recent_articles
from agents.pipeline import run_pipeline
import json

async def main():
    print("Fetching latest article from articles_raw...")
    articles = await get_recent_articles(limit=1)
    if not articles:
        print("No articles found in articles_raw.")
        return
    
    latest_article = articles[0]
    article_id = latest_article["id"]
    title = latest_article["title"]
    print(f"Found article: {title} (ID: {article_id})")
    
    print("Running pipeline...")
    try:
        result = await run_pipeline(article_id=article_id, profile="general")
        print("\n=== PIPELINE RESULT ===\n")
        print(result.model_dump_json(indent=2))
        print("\n=======================\n")
    except Exception as e:
        print(f"Error running pipeline: {e}")

if __name__ == "__main__":
    asyncio.run(main())
