import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from ingestion.gnews import GNewsClient
from pipeline.deduplicator import filter_new_articles
from pipeline.embedder import embed_articles_batch
from db.supabase_client import bulk_insert_articles

async def ingest_20_gnews():
    print("Initializing GNewsClient...")
    client = GNewsClient()
    
    print("Fetching top headlines from GNews with categories...")
    tech = await client.fetch_top(category="technology", max_results=20)
    science = await client.fetch_top(category="science", max_results=20)
    business = await client.fetch_top(category="business", max_results=20)
    
    tech = [a for a in tech if a.image_url][:5]
    science = [a for a in science if a.image_url][:5]
    business = [a for a in business if a.image_url][:5]
    
    raw_articles = tech + science + business
    print(f"Fetched {len(raw_articles)} raw articles containing images from GNews.")
    
    if not raw_articles:
        return
        
    print("Filtering against existing database entries...")
    new_articles, duplicates = await filter_new_articles(raw_articles)
    print(f"New unique articles: {len(new_articles)}, Duplicates skipped: {duplicates}")
    
    if not new_articles:
        print("No new articles to add. Database already has these.")
        return
        
    print("Generating embeddings for new articles...")
    embedded_articles = await embed_articles_batch(new_articles)
    
    print("Inserting into Supabase database with img_url mapping...")
    inserted_count = await bulk_insert_articles(embedded_articles)
    print(f"Successfully inserted {inserted_count} articles into DB!")

if __name__ == "__main__":
    asyncio.run(ingest_20_gnews())
