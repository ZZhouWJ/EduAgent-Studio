-- ============================================================
-- PostgreSQL 迁移脚本：MySQL → PostgreSQL (A3 业务表)
-- EduAgent Studio - Phase 3 PostgreSQL 迁移
-- ============================================================
-- 使用方法：
--   psql -h localhost -U postgres -d eduagent_studio -f 11_postgresql_migration.sql
--
-- 前置条件：
--   1. docker-compose up -d postgres  (已配置 PostgreSQL 16 + pgvector)
--   2. MySQL 数据通过 mysqldump 导出为 CSV，然后 COPY 进 PostgreSQL
-- ============================================================

-- -----------------------------------------------
-- 1. courses 课程表
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_name VARCHAR(200) NOT NULL,
    course_code VARCHAR(50),
    description TEXT,
    teacher_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'draft')),
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
COMMENT ON TABLE courses IS '课程表';
COMMENT ON COLUMN courses.course_id IS '课程ID（手动指定，与 MySQL ID 一致）';
COMMENT ON COLUMN courses.course_name IS '课程名称';
COMMENT ON COLUMN courses.course_code IS '课程代码';
COMMENT ON COLUMN courses.status IS '课程状态: active/archived/draft';

CREATE INDEX IF NOT EXISTS idx_courses_teacher ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_status_deleted ON courses(status, is_deleted);

-- -----------------------------------------------
-- 2. knowledge_points 知识点表
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_points (
    kp_id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    kp_name VARCHAR(200) NOT NULL,
    kp_code VARCHAR(50),
    parent_kp_id INTEGER,
    difficulty_level VARCHAR(20) NOT NULL DEFAULT 'basic' CHECK (difficulty_level IN ('basic', 'intermediate', 'advanced')),
    description TEXT,
    estimated_hours DECIMAL(5,2),
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
COMMENT ON TABLE knowledge_points IS '知识点表';
COMMENT ON COLUMN knowledge_points.kp_id IS '知识点ID（手动指定，与 MySQL ID 一致）';
COMMENT ON COLUMN knowledge_points.difficulty_level IS '难度等级: basic/intermediate/advanced';
COMMENT ON COLUMN knowledge_points.estimated_hours IS '预计学习时长（小时）';

CREATE INDEX IF NOT EXISTS idx_kp_course ON knowledge_points(course_id);
CREATE INDEX IF NOT EXISTS idx_kp_parent ON knowledge_points(parent_kp_id);
CREATE INDEX IF NOT EXISTS idx_kp_difficulty ON knowledge_points(difficulty_level);

-- -----------------------------------------------
-- 3. student_profiles 学生画像表
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS student_profiles (
    profile_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    learning_goal TEXT,
    current_level TEXT,
    interests VARCHAR(500),
    resource_preferences VARCHAR(500),
    weekly_hours INTEGER,
    mastery_score DECIMAL(5,3) NOT NULL DEFAULT 0.000,
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (student_id, course_id)
);
COMMENT ON TABLE student_profiles IS '学生画像表';
COMMENT ON COLUMN student_profiles.mastery_score IS '综合掌握度评分（0-1）';

CREATE INDEX IF NOT EXISTS idx_profile_course ON student_profiles(course_id);
CREATE INDEX IF NOT EXISTS idx_profile_mastery ON student_profiles(mastery_score);

-- -----------------------------------------------
-- 4. student_knowledge_mastery 学生知识点掌握度表
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS student_knowledge_mastery (
    mastery_id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES student_profiles(profile_id),
    kp_id INTEGER NOT NULL REFERENCES knowledge_points(kp_id),
    mastery_level DECIMAL(5,3) NOT NULL DEFAULT 0.000,
    last_test_score DECIMAL(5,3),
    last_test_date DATE,
    update_reason VARCHAR(255),
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (profile_id, kp_id)
);
COMMENT ON TABLE student_knowledge_mastery IS '学生知识点掌握度表';

CREATE INDEX IF NOT EXISTS idx_mastery_kp ON student_knowledge_mastery(kp_id);
CREATE INDEX IF NOT EXISTS idx_mastery_level ON student_knowledge_mastery(mastery_level);

-- -----------------------------------------------
-- 5. learning_resources 学习资源表
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS learning_resources (
    resource_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    resource_title VARCHAR(200) NOT NULL,
    resource_type VARCHAR(20) NOT NULL CHECK (resource_type IN ('lecture', 'ppt', 'quiz', 'case', 'review', 'test', 'other')),
    difficulty VARCHAR(20) NOT NULL DEFAULT 'basic' CHECK (difficulty IN ('basic', 'intermediate', 'advanced')),
    content TEXT,
    target_kp_ids VARCHAR(500),
    generation_model VARCHAR(100),
    generation_agent VARCHAR(100),
    invocation_id BIGINT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_review', 'approved', 'rejected', 'archived')),
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_at TIMESTAMP
);
COMMENT ON TABLE learning_resources IS '学习资源表';
COMMENT ON COLUMN learning_resources.resource_type IS '资源类型: lecture/ppt/quiz/case/review/test/other';
COMMENT ON COLUMN learning_resources.status IS '审核状态: draft/pending_review/approved/rejected/archived';

CREATE INDEX IF NOT EXISTS idx_resource_course ON learning_resources(course_id);
CREATE INDEX IF NOT EXISTS idx_resource_type ON learning_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resource_status ON learning_resources(status, is_deleted);
CREATE INDEX IF NOT EXISTS idx_resource_created ON learning_resources(created_at);

-- -----------------------------------------------
-- 6. learning_feedbacks 学习反馈表
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS learning_feedbacks (
    feedback_id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES student_profiles(profile_id),
    resource_id INTEGER REFERENCES learning_resources(resource_id),
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    feedback_type VARCHAR(30) NOT NULL CHECK (feedback_type IN ('quiz_result', 'self_report', 'study_note', 'question')),
    content TEXT,
    quiz_score DECIMAL(5,3),
    self_mastery DECIMAL(5,3),
    difficulty_rating VARCHAR(20) CHECK (difficulty_rating IN ('too_easy', 'appropriate', 'too_hard')),
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
COMMENT ON TABLE learning_feedbacks IS '学习反馈表';

CREATE INDEX IF NOT EXISTS idx_feedback_profile ON learning_feedbacks(profile_id);
CREATE INDEX IF NOT EXISTS idx_feedback_resource ON learning_feedbacks(resource_id);
CREATE INDEX IF NOT EXISTS idx_feedback_course ON learning_feedbacks(course_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON learning_feedbacks(created_at);

-- -----------------------------------------------
-- 7. learning_tasks 学习任务表
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS learning_tasks (
    task_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    target_kp_ids VARCHAR(500),
    creator_id INTEGER NOT NULL,
    assignee_id INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'assigned', 'in_progress', 'completed', 'archived')),
    due_date TIMESTAMP,
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
COMMENT ON TABLE learning_tasks IS '学习任务表';

CREATE INDEX IF NOT EXISTS idx_task_course ON learning_tasks(course_id);
CREATE INDEX IF NOT EXISTS idx_task_assignee ON learning_tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_task_status ON learning_tasks(status, is_deleted);

-- -----------------------------------------------
-- 8. 数据迁移（从 MySQL 导出后的手动 INSERT）
-- -----------------------------------------------

-- courses 数据（来自 10_insert_a3_initial_data.sql）
INSERT INTO courses (course_id, course_name, course_code, description, teacher_id, status, created_at) VALUES
    (1, '数据库系统原理', 'CS301', '系统学习数据库系统的基本概念、关系模型、SQL语言、事务与并发控制、数据库设计等内容', 1, 'active', CURRENT_TIMESTAMP),
    (2, 'Python程序设计', 'CS201', 'Python编程语言基础、函数、模块、面向对象、异常处理等核心内容', 1, 'active', CURRENT_TIMESTAMP),
    (3, '软件工程实践', 'CS401', '软件工程方法论、需求分析、系统设计、项目管理、敏捷开发等内容', 1, 'active', CURRENT_TIMESTAMP)
ON CONFLICT (course_id) DO UPDATE SET
    course_name = EXCLUDED.course_name,
    course_code = EXCLUDED.course_code,
    description = EXCLUDED.description;

-- knowledge_points 数据
INSERT INTO knowledge_points (kp_id, course_id, kp_name, kp_code, difficulty_level, description, estimated_hours, created_at) VALUES
    -- 数据库系统原理
    (1,  1, '关系模型基础', 'DB001', 'basic', '关系模型的核心概念：关系、元组、属性、键', 2.0, CURRENT_TIMESTAMP),
    (2,  1, 'SQL基本查询', 'DB002', 'basic', 'SELECT/FROM/WHERE/ORDER BY等基本查询语法', 3.0, CURRENT_TIMESTAMP),
    (3,  1, '数据定义DDL', 'DB003', 'basic', 'CREATE/ALTER/DROP TABLE等DDL语句', 2.0, CURRENT_TIMESTAMP),
    (5,  1, 'SQL多表连接', 'DB005', 'intermediate', 'INNER JOIN/LEFT JOIN/RIGHT JOIN/FULL OUTER JOIN等', 4.0, CURRENT_TIMESTAMP),
    (8,  1, '事务隔离级别', 'DB008', 'advanced', 'ACID特性、脏读/不可重复读/幻读、四种隔离级别', 3.0, CURRENT_TIMESTAMP),
    (12, 1, '数据库范式', 'DB012', 'intermediate', '1NF/2NF/3NF/BCNF范式及规范化过程', 3.0, CURRENT_TIMESTAMP),
    (15, 1, '索引与优化', 'DB015', 'advanced', 'B+树索引、索引设计原则、查询优化基础', 4.0, CURRENT_TIMESTAMP),
    (20, 1, '数据库设计', 'DB020', 'intermediate', 'ER图设计、概念模型、逻辑设计、物理设计', 4.0, CURRENT_TIMESTAMP),
    -- Python程序设计
    (20, 2, 'Python基础语法', 'PY001', 'basic', '变量、数据类型、运算符、流程控制', 3.0, CURRENT_TIMESTAMP),
    (21, 2, '函数参数传递', 'PY002', 'intermediate', '位置参数、关键字参数、默认参数、*args/**kwargs', 2.5, CURRENT_TIMESTAMP),
    (22, 2, '模块导入', 'PY003', 'intermediate', 'import/from...import、模块搜索路径、包管理', 2.0, CURRENT_TIMESTAMP),
    (23, 2, '异常处理', 'PY004', 'intermediate', 'try/except/finally、自定义异常', 2.0, CURRENT_TIMESTAMP),
    -- 软件工程实践
    (30, 3, '需求分析', 'SE001', 'basic', '需求获取、需求建模、需求规格说明', 3.0, CURRENT_TIMESTAMP),
    (31, 3, 'UML建模', 'SE002', 'intermediate', '用例图、类图、时序图、活动图等', 4.0, CURRENT_TIMESTAMP)
ON CONFLICT (kp_id) DO UPDATE SET
    kp_name = EXCLUDED.kp_name,
    course_id = EXCLUDED.course_id,
    difficulty_level = EXCLUDED.difficulty_level,
    estimated_hours = EXCLUDED.estimated_hours;

-- learning_tasks 数据
INSERT INTO learning_tasks (task_id, course_id, title, description, target_kp_ids, creator_id, status, created_at) VALUES
    (1, 1, '数据库事务与并发控制', '学习事务的ACID特性，掌握四种隔离级别的区别和应用场景', '8', 1, 'assigned', CURRENT_TIMESTAMP),
    (2, 1, 'SQL多表连接练习', '完成教务系统多表查询练习，包括INNER JOIN和LEFT JOIN', '5', 1, 'assigned', CURRENT_TIMESTAMP),
    (3, 2, 'Python函数与模块练习', '编写一个包含多个函数的Python模块，实现基本的文本处理功能', '21,22', 1, 'assigned', CURRENT_TIMESTAMP),
    (4, 3, 'UML建模实践', '使用UML工具为选定的系统绘制完整的用例图和类图', '31', 1, 'draft', CURRENT_TIMESTAMP)
ON CONFLICT (task_id) DO UPDATE SET
    title = EXCLUDED.title,
    status = EXCLUDED.status;

-- -----------------------------------------------
-- 9. 验证查询
-- -----------------------------------------------
DO $$
BEGIN
    RAISE NOTICE '=== PostgreSQL A3 迁移验证 ===';
    RAISE NOTICE 'courses: %', (SELECT COUNT(*) FROM courses);
    RAISE NOTICE 'knowledge_points: %', (SELECT COUNT(*) FROM knowledge_points);
    RAISE NOTICE 'learning_tasks: %', (SELECT COUNT(*) FROM learning_tasks);
    RAISE NOTICE 'learning_resources: %', (SELECT COUNT(*) FROM learning_resources);
    RAISE NOTICE 'learning_feedbacks: %', (SELECT COUNT(*) FROM learning_feedbacks);
    RAISE NOTICE 'student_profiles: %', (SELECT COUNT(*) FROM student_profiles);
    RAISE NOTICE 'student_knowledge_mastery: %', (SELECT COUNT(*) FROM student_knowledge_mastery);
END $$;

-- MySQL → PostgreSQL 迁移完成
-- 如需从现有 MySQL 迁移数据，执行以下步骤：
--   1. mysqldump -h 127.0.0.1 -P 3306 -u root -p061202 \
--      ai_collab_audit_system courses knowledge_points learning_tasks \
--      student_profiles student_knowledge_mastery learning_resources learning_feedbacks \
--      --where="is_deleted=0" --no-create-info > a3_data.sql
--   2. sed -i 's/`//g; s/\\r\\n/ /g' a3_data.sql  # 清理 MySQL 语法
--   3. psql -h localhost -U postgres -d eduagent_studio -f a3_data.sql
