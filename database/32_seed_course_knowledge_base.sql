-- Seed a complete, reviewable CS301 course knowledge base with numeric chunk IDs.
-- The source dataset is tracked at database/fixtures/database_system_principles.md.

SET @course_id := (
    SELECT course_id FROM courses
    WHERE course_code = 'CS301' AND is_deleted = 0
    ORDER BY course_id LIMIT 1
);
SET @seed_filename := 'database_system_principles.md';

INSERT INTO course_materials
    (course_id, filename, file_type, storage_path, status, total_chunks,
     created_by, is_deleted, material_version, total_chars, last_reparse_at)
SELECT
    @course_id, @seed_filename, 'markdown',
    'database/fixtures/database_system_principles.md', 'parsed', 9,
    0, 0, 1, 0, NOW()
FROM DUAL
WHERE @course_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM course_materials
      WHERE course_id = @course_id AND filename = @seed_filename AND is_deleted = 0
  );

SET @material_id := (
    SELECT material_id FROM course_materials
    WHERE course_id = @course_id AND filename = @seed_filename AND is_deleted = 0
    ORDER BY material_id LIMIT 1
);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_db_intro' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '数据库基本概念',
       '数据库是按数据模型组织、长期存储并可被多个用户共享的数据集合。数据库管理系统 DBMS 负责数据定义、查询、更新、并发控制、完整性与故障恢复。三级模式包含外模式、模式和内模式，逻辑独立性与物理独立性使应用不必随底层局部变化而改写。',
       1, '数据库,DBMS,三级模式,数据独立性', 1, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=1 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_relational_model' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '关系模型',
       '关系可视为二维表，行称为元组，列称为属性，属性的取值范围称为域。候选键是能唯一识别元组的最小属性集，主键是选定的候选键，外键用于引用另一关系的主键。完整性包括实体完整性、参照完整性和用户定义完整性。',
       2, '关系模型,元组,属性,主键,外键,完整性', 2, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=2 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_sql_basic' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, 'SQL 基本查询',
       'SQL 查询的基本结构是 SELECT FROM WHERE。WHERE 在分组前过滤行，GROUP BY 建立分组，HAVING 在分组后过滤，ORDER BY 对最终结果排序。COUNT、SUM、AVG、MAX 和 MIN 是常用聚合函数。空值应使用 IS NULL 判断，不能用等号与空值比较。',
       3, 'SQL,SELECT,WHERE,GROUP BY,HAVING,聚合函数,空值', 3, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=3 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_sql_join' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '多表连接与子查询',
       '内连接只保留满足连接条件的行；左外连接保留左表全部行，右表无匹配时补空值。忘记连接条件会产生笛卡尔积。子查询可返回标量、一列或临时表，EXISTS 关心子查询是否返回行。在语义等价时应结合执行计划选择连接或子查询。',
       4, '内连接,外连接,子查询,EXISTS,笛卡尔积', 4, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=4 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_index' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '索引与查询优化',
       'B+ 树索引适合等值、范围和排序查询。联合索引遵循最左前缀原则，覆盖索引可减少回表。索引会占用存储并增加写入维护成本，不是越多越好。应使用 EXPLAIN 观察访问类型、扫描行数、选用索引和额外操作。',
       5, '索引,B+树,联合索引,最左前缀,覆盖索引,EXPLAIN', 5, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=5 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_transaction' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '事务与 ACID',
       '事务是不可分割的逻辑工作单元。原子性要求操作要么全部提交、要么全部回滚；一致性要求事务保持业务约束；隔离性要求并发事务不暴露不应见的中间状态；持久性要求已提交结果在故障后仍可恢复。银行转账中的扣款和入账必须放在同一事务中。',
       6, '事务,ACID,原子性,一致性,隔离性,持久性,转账', 6, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=6 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_concurrency' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '并发控制与锁',
       '并发执行可能造成脏读、不可重复读、幻读和丢失更新。SQL 标准定义读未提交、读已提交、可重复读和串行化四个隔离级别。共享锁允许并发读，排他锁用于写入并阻止冲突访问。死锁应通过统一加锁顺序、缩短事务、死锁检测与超时回滚处理。',
       7, '并发控制,隔离级别,共享锁,排他锁,死锁,MVCC', 7, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=7 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_norm' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '范式与反范式',
       '第一范式要求属性值不可再分；第二范式消除非主属性对候选键的部分依赖；第三范式消除非主属性对候选键的传递依赖。分解应兼顾无损连接和依赖保持。反范式是在明确性能瓶颈和一致性维护方案后有意引入冗余。',
       8, '第一范式,第二范式,第三范式,BCNF,无损连接,反范式', 8, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=8 AND is_deleted=0);

SET @kp_id := (SELECT kp_id FROM knowledge_points WHERE course_id=@course_id AND kp_code='kp_design' AND is_deleted=0 LIMIT 1);
INSERT INTO course_material_chunks
    (material_id, course_id, kp_id, title, content, source_page, bm25_terms, chunk_index, is_deleted, material_version)
SELECT @material_id, @course_id, @kp_id, '数据库设计 (E-R)',
       '数据库设计依次经过需求分析、概念结构设计、逻辑结构设计、物理结构设计、实现和运行维护。E-R 模型用实体、属性和联系描述业务语义。一对多联系通常在多端加入一端主键作为外键，多对多联系需建立中间表保存两端外键和联系属性。',
       9, '数据库设计,E-R,实体,属性,联系,逻辑设计,外键', 9, 0, 1
FROM DUAL WHERE @material_id IS NOT NULL AND @kp_id IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM course_material_chunks WHERE material_id=@material_id AND chunk_index=9 AND is_deleted=0);

INSERT INTO kp_chunk_links
    (chunk_id, kp_id, match_method, relevance_score, status, match_version)
SELECT chunk_id, kp_id, 'manual', 1.0000, 'confirmed', 1
FROM course_material_chunks
WHERE material_id=@material_id AND kp_id IS NOT NULL AND is_deleted=0
ON DUPLICATE KEY UPDATE
    match_method=VALUES(match_method),
    relevance_score=VALUES(relevance_score),
    status=VALUES(status),
    match_version=VALUES(match_version);

UPDATE course_materials m
SET m.status='parsed',
    m.total_chunks=(SELECT COUNT(*) FROM course_material_chunks c WHERE c.material_id=m.material_id AND c.is_deleted=0),
    m.total_chars=(SELECT COALESCE(SUM(CHAR_LENGTH(c.content)),0) FROM course_material_chunks c WHERE c.material_id=m.material_id AND c.is_deleted=0),
    m.last_reparse_at=NOW()
WHERE m.material_id=@material_id;
