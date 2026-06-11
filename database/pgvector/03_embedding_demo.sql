-- ============================================================
-- 向量检索 Demo
-- ============================================================

-- 插入示例 embedding（768维随机向量，仅供演示）
-- 实际使用时用真实 embedding 模型生成向量

-- 示例：插入 SQL 多表连接相关知识点 embedding
-- INSERT INTO knowledge_point_embeddings (kp_id, content_chunk, embedding)
-- VALUES (5, 'SQL多表连接：INNER JOIN返回两表匹配记录，LEFT JOIN返回左表全部记录',
--   '[0.1,0.2,...]'::vector);

-- 查询最相似的知识点（余弦相似度）
-- SELECT
--     kp.kp_name,
--     kp.difficulty_level,
--     1 - (e.embedding <=> '[query_vector]'::vector) AS similarity
-- FROM knowledge_point_embeddings e
-- JOIN knowledge_points kp ON e.kp_id = kp.kp_id
-- ORDER BY e.embedding <=> '[query_vector]'::vector
-- LIMIT 5;
