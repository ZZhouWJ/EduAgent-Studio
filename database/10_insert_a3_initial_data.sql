-- ============================================================
-- 10_insert_a3_initial_data.sql
-- EduAgent Studio - A3 赛题初始化数据
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 插入课程数据
-- ============================================================
INSERT INTO `courses` (`course_name`, `course_code`, `description`, `teacher_id`, `status`) VALUES
    ('数据库系统原理', 'CS301', '系统学习数据库系统的基本概念、关系模型、SQL语言、事务与并发控制、数据库设计等内容', 1, 'active'),
    ('Python程序设计', 'CS201', 'Python编程语言基础、函数、模块、面向对象、异常处理等核心内容', 1, 'active'),
    ('软件工程实践', 'CS401', '软件工程方法论、需求分析、系统设计、项目管理、敏捷开发等内容', 1, 'active');

-- ============================================================
-- 插入知识点数据
-- ============================================================
INSERT INTO `knowledge_points` (`course_id`, `kp_name`, `kp_code`, `difficulty_level`, `description`, `estimated_hours`) VALUES
    -- 数据库系统原理
    (1, '关系模型基础', 'DB001', 'basic', '关系模型的核心概念：关系、元组、属性、键', 2.0),
    (1, 'SQL基本查询', 'DB002', 'basic', 'SELECT/FROM/WHERE/ORDER BY等基本查询语法', 3.0),
    (1, '数据定义DDL', 'DB003', 'basic', 'CREATE/ALTER/DROP TABLE等DDL语句', 2.0),
    (1, 'SQL多表连接', 'DB005', 'intermediate', 'INNER JOIN/LEFT JOIN/RIGHT JOIN/FULL OUTER JOIN等', 4.0),
    (1, '事务隔离级别', 'DB008', 'advanced', 'ACID特性、脏读/不可重复读/幻读、四种隔离级别', 3.0),
    (1, '数据库范式', 'DB012', 'intermediate', '1NF/2NF/3NF/BCNF范式及规范化过程', 3.0),
    (1, '索引与优化', 'DB015', 'advanced', 'B+树索引、索引设计原则、查询优化基础', 4.0),
    (1, '数据库设计', 'DB020', 'intermediate', 'ER图设计、概念模型、逻辑设计、物理设计', 4.0),
    -- Python程序设计
    (2, 'Python基础语法', 'PY001', 'basic', '变量、数据类型、运算符、流程控制', 3.0),
    (2, '函数参数传递', 'PY002', 'intermediate', '位置参数、关键字参数、默认参数、*args/**kwargs', 2.5),
    (2, '模块导入', 'PY003', 'intermediate', 'import/from...import、模块搜索路径、包管理', 2.0),
    (2, '异常处理', 'PY004', 'intermediate', 'try/except/finally、自定义异常', 2.0),
    -- 软件工程实践
    (3, '需求分析', 'SE001', 'basic', '需求获取、需求建模、需求规格说明', 3.0),
    (3, 'UML建模', 'SE002', 'intermediate', '用例图、类图、时序图、活动图等', 4.0);

-- ============================================================
-- 插入学习任务数据
-- ============================================================
INSERT INTO `learning_tasks` (`course_id`, `title`, `description`, `target_kp_ids`, `creator_id`, `status`) VALUES
    (1, '数据库事务与并发控制', '学习事务的ACID特性，掌握四种隔离级别的区别和应用场景', '8', 1, 'assigned'),
    (1, 'SQL多表连接练习', '完成教务系统多表查询练习，包括INNER JOIN和LEFT JOIN', '5', 1, 'assigned'),
    (2, 'Python函数与模块练习', '编写一个包含多个函数的Python模块，实现基本的文本处理功能', '2,3', 1, 'assigned'),
    (3, 'UML建模实践', '使用UML工具为选定的系统绘制完整的用例图和类图', '2', 1, 'draft');

-- ============================================================
-- 插入 A3 提示词模板类型
-- ============================================================
UPDATE `task_types` SET `type_name` = '知识点讲义生成', `type_code` = 'lecture_generation', `description` = '根据知识点和学习目标，生成个性化的知识点讲义' WHERE `type_code` = 'requirement_analysis';

INSERT INTO `task_types` (`type_name`, `type_code`, `description`, `status`) VALUES
    ('PPT大纲生成', 'ppt_generation', '根据课程内容生成PPT演示大纲', 'active'),
    ('习题与答案生成', 'quiz_generation', '根据知识点生成配套练习题和答案解析', 'active'),
    ('案例材料生成', 'case_generation', '根据知识点生成实际应用案例', 'active'),
    ('复习计划生成', 'review_plan_generation', '根据学生薄弱点生成个性化复习计划', 'active'),
    ('阶段测验生成', 'test_generation', '根据学习进度生成阶段测验题目', 'active');
