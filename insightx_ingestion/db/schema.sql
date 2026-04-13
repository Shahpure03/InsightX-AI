-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
 
 
-- 2. CORE INGESTION LAYER
-- CHANGE vs old schema: removed embedding column (now in article_embeddings)
--                       added status column for active/archived lifecycle
CREATE TABLE IF NOT EXISTS articles_raw (
  id            uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  title         text        NOT NULL,
  content       text        NOT NULL,
  url           text        UNIQUE NOT NULL,
  source        text        NOT NULL,
  published_at  timestamptz NOT NULL,
  author        text,
  image_url     text,
  category      text,
  language      text        DEFAULT 'en',
  country       text,
  video_id      text,
  thumbnail     text,
  content_hash  text        UNIQUE NOT NULL,
  status        text        NOT NULL DEFAULT 'active', -- 'active' | 'archived'
  ingested_at   timestamptz DEFAULT now()
);
 
-- Embeddings live here, NOT inside articles_raw
-- This table is NEVER hard-deleted — archived articles keep their vector
CREATE TABLE IF NOT EXISTS article_embeddings (
  article_id  uuid PRIMARY KEY REFERENCES articles_raw(id) ON DELETE CASCADE,
  embedding   vector(768),                         -- nomic-embed-text-v1_5 (Groq)
  model_used  text DEFAULT 'nomic-embed-text-v1_5',
  created_at  timestamptz DEFAULT now()
);
 
 
-- 3. PIPELINE TRACKING
-- One row per article — tracks which agent stages have completed
-- Created immediately after article insert
-- Makes pipeline resumable if any agent crashes mid-batch
CREATE TABLE IF NOT EXISTS article_pipeline_states (
  article_id           uuid PRIMARY KEY REFERENCES articles_raw(id) ON DELETE CASCADE,
  event_extracted      boolean DEFAULT false,
  reasoning_done       boolean DEFAULT false,
  enrichment_done      boolean DEFAULT false,  -- categories/entities/sentiment
  action_template_done boolean DEFAULT false,
  prediction_done      boolean DEFAULT false,
  last_processed_at    timestamptz,
  retry_count          int DEFAULT 0,
  error                text
);
 
 
-- 4. ENRICHMENT LAYER (Global — computed once, same for all users)
-- Event Agent and Reasoning Agent write here
-- Personalization Agent reads from here before adding user-specific layer
CREATE TABLE IF NOT EXISTS articles_enriched (
  article_id        uuid PRIMARY KEY REFERENCES articles_raw(id) ON DELETE CASCADE,
  categories        text[],
  entities          text[],
  sentiment         float,          -- -1.0 (panic) to +1.0 (optimism)
  sentiment_label   text,           -- 'panic' | 'neutral' | 'optimism'
  event_output      jsonb,          -- { "event": "...", "actors": [], "location": "..." }
  reasoning_output  jsonb,          -- { "cause": "...", "effect": "...", "impact_sectors": [] }
  processed_at      timestamptz DEFAULT now()
);
 
 
-- 5. USER LAYER
 
CREATE TABLE IF NOT EXISTS users (
  id                uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
  email             text    UNIQUE NOT NULL,
  display_name      text,
  active_profile    text    NOT NULL DEFAULT 'student',
  profiles_unlocked text[]  DEFAULT ARRAY['student'],
  created_at        timestamptz DEFAULT now()
);
 
-- One row per user per profile type
-- interest_vector is 768-dim to match Groq nomic-embed-text-v1.5
CREATE TABLE IF NOT EXISTS user_interest_profiles (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          uuid REFERENCES users(id) ON DELETE CASCADE,
  profile_type     text NOT NULL,             -- 'student' | 'explorer' | 'investor'
  selected_topics  text[],                    -- explicit selections
  topic_weights    jsonb,                     -- {"science":1.4,"startup":1.2,"tech":1.6}
  interest_vector  vector(768),              -- weighted avg of topic embeddings
  last_updated     timestamptz DEFAULT now(),
  UNIQUE(user_id, profile_type)
);
 
-- Implicit reading signal — grows with every article read in that topic
-- weight formula: LEAST(1.0 + LN(1 + read_count) * 0.15, 2.0)
CREATE TABLE IF NOT EXISTS user_topic_history (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE,
  topic           text,
  read_count      int   DEFAULT 0,
  weight          float DEFAULT 1.0,
  last_interacted timestamptz,
  UNIQUE(user_id, topic)
);
 
-- Every article-open event logged here
-- profile_at_read tracks which profile was active (user can switch)
CREATE TABLE IF NOT EXISTS user_reading_history (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE,
  article_id      uuid REFERENCES articles_raw(id) ON DELETE CASCADE,
  profile_at_read text,
  seconds_spent   int,
  completed       boolean,
  bookmarked      boolean,
  relevance_score float,    -- cosine similarity at time of read
  read_at         timestamptz DEFAULT now()
);
 
 
-- 6. PERSONALIZATION OUTPUT (User-specific, cached)
-- One row per (article, user, profile_type)
-- Cache hit → serve instantly (0 LLM calls)
-- Cache miss → run agents 3+4+5, insert, return
-- event_output + reasoning_output NOT stored here — they're in articles_enriched
CREATE TABLE IF NOT EXISTS insights (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id             uuid REFERENCES articles_raw(id) ON DELETE CASCADE,
  user_id                uuid REFERENCES users(id)        ON DELETE CASCADE,
  profile_type           text NOT NULL,
 
  personalization_output jsonb,   -- profile-specific angle, tone, framing
  action_output          jsonb,   -- suggested tools + next steps
  prediction_output      jsonb,   -- forward-looking signals + historical analogy
 
  hallucination_score    float,   -- vectara HHEM score; reject < 0.6
  generated_at           timestamptz DEFAULT now(),
 
  UNIQUE(article_id, user_id, profile_type)
);
 
 
-- 7. ARCHIVAL LAYER
-- Nightly job writes here BEFORE flipping articles_raw.status to 'archived'
-- article_embeddings are NOT touched — vectors survive for historical search
CREATE TABLE IF NOT EXISTS article_archive (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id     uuid,           -- intentionally NOT a FK (row stays in articles_raw)
  archive_reason text,           -- 'age' | 'manual' | 'duplicate'
  snapshot       jsonb,          -- full row_to_json() snapshot at archive time
  archived_at    timestamptz DEFAULT now()
);
 
 
-- 8. INGESTION LOGS (unchanged)
CREATE TABLE IF NOT EXISTS ingestion_logs (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_at             timestamptz DEFAULT now(),
  total_fetched      int,
  duplicates_skipped int,
  new_articles       int,
  sources_used       text[],
  errors             text[],
  duration_seconds   float
);
 
 
-- ============================================================
-- 9. INDEXES
-- ============================================================
 
-- Vector search on article embeddings (separated from articles_raw)
CREATE INDEX IF NOT EXISTS article_embedding_idx
  ON article_embeddings USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
 
-- User interest vector index
CREATE INDEX IF NOT EXISTS user_interest_vector_idx
  ON user_interest_profiles USING ivfflat (interest_vector vector_cosine_ops)
  WITH (lists = 10);
 
-- Feed queries
CREATE INDEX IF NOT EXISTS articles_published_idx ON articles_raw (published_at DESC);
CREATE INDEX IF NOT EXISTS articles_category_idx  ON articles_raw (category);
CREATE INDEX IF NOT EXISTS articles_status_idx    ON articles_raw (status);
CREATE INDEX IF NOT EXISTS articles_lang_idx      ON articles_raw (category, language);
 
-- Pipeline worker — find articles pending each stage
CREATE INDEX IF NOT EXISTS pipeline_event_idx
  ON article_pipeline_states (event_extracted) WHERE event_extracted = false;
CREATE INDEX IF NOT EXISTS pipeline_reasoning_idx
  ON article_pipeline_states (reasoning_done) WHERE reasoning_done = false;
 
-- Insight cache lookup
CREATE INDEX IF NOT EXISTS insights_cache_idx
  ON insights (article_id, user_id, profile_type);
 
-- User queries
CREATE INDEX IF NOT EXISTS user_profile_idx
  ON user_interest_profiles (user_id, profile_type);
CREATE INDEX IF NOT EXISTS user_topic_idx
  ON user_topic_history (user_id, topic);
CREATE INDEX IF NOT EXISTS user_reading_idx
  ON user_reading_history (user_id, read_at DESC);
 
 
-- ============================================================
-- 10. FUNCTIONS
-- ============================================================
 
-- Semantic search — now joins article_embeddings separately
-- Added active_only param to optionally include archived articles (for analogy search)
CREATE OR REPLACE FUNCTION search_articles(
  query_embedding  vector(768),
  match_threshold  float   DEFAULT 0.7,
  match_count      int     DEFAULT 10,
  filter_category  text    DEFAULT NULL,
  filter_language  text    DEFAULT 'en',
  active_only      boolean DEFAULT true
)
RETURNS TABLE (
  id           uuid,
  title        text,
  url          text,
  source       text,
  published_at timestamptz,
  category     text,
  similarity   float
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    ar.id, ar.title, ar.url, ar.source,
    ar.published_at, ar.category,
    ROUND((1 - (ae.embedding <=> query_embedding))::numeric, 4)::float AS similarity
  FROM   articles_raw ar
  JOIN   article_embeddings ae ON ar.id = ae.article_id
  WHERE  (filter_category IS NULL OR ar.category = filter_category)
    AND  ar.language = filter_language
    AND  (NOT active_only OR ar.status = 'active')
    AND  1 - (ae.embedding <=> query_embedding) > match_threshold
  ORDER BY ae.embedding <=> query_embedding
  LIMIT  match_count;
END;
$$;
 
 
-- Personalised feed — cosine similarity between article and user's interest vector
CREATE OR REPLACE FUNCTION get_personalised_feed(
  p_user_id   uuid,
  p_profile   text,
  p_limit     int DEFAULT 20
)
RETURNS TABLE (
  article_id      uuid,
  title           text,
  category        text,
  source          text,
  published_at    timestamptz,
  relevance_score float
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    ar.id,
    ar.title,
    ar.category,
    ar.source,
    ar.published_at,
    ROUND((1 - (ae.embedding <=> uip.interest_vector))::numeric, 3)::float AS relevance_score
  FROM   articles_raw ar
  JOIN   article_embeddings ae ON ae.article_id = ar.id
  JOIN   user_interest_profiles uip
           ON uip.user_id = p_user_id
          AND uip.profile_type = p_profile
  WHERE  ar.status = 'active'
  ORDER BY ae.embedding <=> uip.interest_vector
  LIMIT  p_limit;
END;
$$;
 
 
-- Archive job — run nightly at 02:00 IST via pg_cron or external cron
-- Replaces delete_articles_older_than() in supabase_client.py
CREATE OR REPLACE FUNCTION run_archive_job(older_than_days int DEFAULT 7)
RETURNS int
LANGUAGE plpgsql AS $$
DECLARE
  archived_count int;
BEGIN
  -- Snapshot to article_archive
  INSERT INTO article_archive (article_id, archive_reason, snapshot)
  SELECT id, 'age', row_to_json(articles_raw.*)::jsonb
  FROM   articles_raw
  WHERE  published_at < now() - (older_than_days || ' days')::interval
    AND  status = 'active';
 
  GET DIAGNOSTICS archived_count = ROW_COUNT;
 
  -- Flip status (do NOT delete rows, do NOT touch article_embeddings)
  UPDATE articles_raw
  SET    status = 'archived'
  WHERE  published_at < now() - (older_than_days || ' days')::interval
    AND  status = 'active';
 
  RETURN archived_count;
END;
$$;
 