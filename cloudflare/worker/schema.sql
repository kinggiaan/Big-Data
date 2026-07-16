-- D1 Schema for Academic Paper Search
-- Replaces Elasticsearch index with SQLite + FTS5

-- Main papers table
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    authors TEXT DEFAULT '',
    year TEXT DEFAULT '',
    categories TEXT DEFAULT ''
);

-- Full-Text Search virtual table (replaces BM25 in Elasticsearch)
-- tokenize='porter unicode61' provides English stemming similar to ES academic_english analyzer
CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
    title,
    abstract,
    content='papers',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

-- Triggers to keep FTS in sync with main table
CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
    INSERT INTO papers_fts(rowid, title, abstract)
    VALUES (new.rowid, new.title, new.abstract);
END;

CREATE TRIGGER IF NOT EXISTS papers_ad AFTER DELETE ON papers BEGIN
    INSERT INTO papers_fts(papers_fts, rowid, title, abstract)
    VALUES ('delete', old.rowid, old.title, old.abstract);
END;

CREATE TRIGGER IF NOT EXISTS papers_au AFTER UPDATE ON papers BEGIN
    INSERT INTO papers_fts(papers_fts, rowid, title, abstract)
    VALUES ('delete', old.rowid, old.title, old.abstract);
    INSERT INTO papers_fts(rowid, title, abstract)
    VALUES (new.rowid, new.title, new.abstract);
END;

-- Indexes for filter queries
CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_categories ON papers(categories);
