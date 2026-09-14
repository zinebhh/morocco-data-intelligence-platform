-- Se connecter à la base de données analytics
CREATE DATABASE analytics;

\c analytics;

-- Table des publications
CREATE TABLE IF NOT EXISTS publications (
    id VARCHAR(64) PRIMARY KEY,
    openalex_id VARCHAR(255),
    title TEXT NOT NULL,
    publication_year INTEGER,
    publication_date DATE,
    doi VARCHAR(255),
    citation_count INTEGER DEFAULT 0,
    publication_type VARCHAR(50),
    language VARCHAR(10),
    journal VARCHAR(500),
    source_type VARCHAR(50),
    is_open_access BOOLEAN DEFAULT FALSE,
    oa_status VARCHAR(50),
    title_length INTEGER,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_publications_year ON publications(publication_year);
CREATE INDEX idx_publications_type ON publications(publication_type);
CREATE INDEX idx_publications_journal ON publications(journal);
CREATE INDEX idx_publications_oa ON publications(is_open_access);

-- Table des universités
CREATE TABLE IF NOT EXISTS universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    url VARCHAR(500),
    pages_scraped INTEGER DEFAULT 0,
    last_scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Statistiques
CREATE TABLE IF NOT EXISTS analytics_stats (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    metric_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vue pour les KPIs
CREATE OR REPLACE VIEW v_publications_by_year AS
SELECT 
    publication_year,
    COUNT(*) as total_publications,
    SUM(citation_count) as total_citations,
    AVG(citation_count)::NUMERIC(10,2) as avg_citations,
    COUNT(CASE WHEN is_open_access THEN 1 END) as open_access_count
FROM publications
WHERE publication_year IS NOT NULL
GROUP BY publication_year
ORDER BY publication_year DESC;

-- Vue pour les top journaux
CREATE OR REPLACE VIEW v_top_journals AS
SELECT 
    journal,
    COUNT(*) as publications_count,
    SUM(citation_count) as total_citations
FROM publications
WHERE journal IS NOT NULL
GROUP BY journal
ORDER BY publications_count DESC
LIMIT 20;