-- ============================================================
-- 启用 pgvector 扩展（PostgreSQL）
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证扩展是否启用
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
