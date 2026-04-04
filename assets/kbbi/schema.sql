-- KBBI Database Schema for Legal-MD-Converter
-- Optimized for spell checking with FTS5 and Bloom filter support

-- Main kata table with optimized indexing
CREATE TABLE IF NOT EXISTS kata (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    kata TEXT NOT NULL,
    entry_id INTEGER,
    is_bloom_candidate INTEGER DEFAULT 0,
    frequency INTEGER DEFAULT 1
);

-- Standard B-tree index for exact lookups
CREATE INDEX IF NOT EXISTS idx_kata_lower ON kata(LOWER(kata));
CREATE INDEX IF NOT EXISTS idx_kata_freq ON kata(frequency DESC);

-- Unique constraint to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_kata_unique ON kata(LOWER(kata));

-- FTS5 virtual table for fuzzy search
-- (Created programmatically due to FTS specifics)

-- Metadata table for tracking
CREATE TABLE IF NOT EXISTS kbbi_meta (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert version metadata
INSERT OR REPLACE INTO kbbi_meta (key, value) VALUES ('version', '1.0');
INSERT OR REPLACE INTO kbbi_meta (key, value) VALUES ('created', datetime('now'));
INSERT OR REPLACE INTO kbbi_meta (key, value) VALUES ('source', 'KBBI Daring');
