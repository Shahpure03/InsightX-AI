CREATE EXTENSION IF NOT EXISTS vector;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS articles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  content text NOT NULL,
  url text UNIQUE NOT NULL,
  source text NOT NULL,
  published_at timestamptz NOT NULL,
  author text,
  image_url text,
  category text,
  language text DEFAULT 'en',
  country text,
  video_id text,
  thumbnail text,
  content_hash text UNIQUE NOT NULL,
  embedding vector(768),
  ingested_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ingestion_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_at timestamptz DEFAULT now(),
  total_fetched int,
  duplicates_skipped int,
  new_articles int,
  sources_used text[],
  errors text[],
  duration_seconds float
);

CREATE INDEX IF NOT EXISTS articles_embedding_ivfflat_idx
  ON articles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS articles_category_language_idx
  ON articles (category, language);

CREATE INDEX IF NOT EXISTS articles_published_at_desc_idx
  ON articles (published_at DESC);

CREATE OR REPLACE FUNCTION search_articles(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 10,
  filter_category text DEFAULT NULL,
  filter_language text DEFAULT 'en'
)
RETURNS TABLE (
  id uuid,
  title text,
  content text,
  url text,
  source text,
  published_at timestamptz,
  category text,
  similarity float
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    a.id,
    a.title,
    a.content,
    a.url,
    a.source,
    a.published_at,
    a.category,
    1 - (a.embedding <=> query_embedding) AS similarity
  FROM articles a
  WHERE
    (filter_category IS NULL OR a.category = filter_category)
    AND a.language = filter_language
    AND 1 - (a.embedding <=> query_embedding) > match_threshold
  ORDER BY a.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
