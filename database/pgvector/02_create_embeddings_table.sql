-- ============================================================
-- 创建 embedding 表和向量索引
-- ============================================================

CREATE TABLE IF NOT EXISTS knowledge_point_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    kp_id INTEGER NOT NULL,
    content_chunk TEXT NOT NULL,
    embedding VECTOR(768),
    chunk_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 HNSW 索引（推荐）
CREATE INDEX ON knowledge_point_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

COMMENT ON TABLE knowledge_point_embeddings IS '知识点 embedding 存储表';
