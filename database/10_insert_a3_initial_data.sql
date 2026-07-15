-- ============================================================
-- 10_insert_a3_initial_data.sql
-- EduAgent Studio - A3 赛题初始化数据
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 插入课程数据
-- ============================================================
INSERT INTO `courses` (`course_name`, `course_code`, `description`, `teacher_id`, `status`) VALUES
    ('数据库系统原理', 'CS301', '系统学习数据库系统的基本概念、关系模型、SQL语言、事务与并发控制、数据库设计等内容', (SELECT user_id FROM users WHERE username = 'teacher_li'), 'active'),
    ('Python程序设计', 'CS201', 'Python编程语言基础、函数、模块、面向对象、异常处理等核心内容', (SELECT user_id FROM users WHERE username = 'teacher_li'), 'active'),
    ('软件工程实践', 'CS401', '软件工程方法论、需求分析、系统设计，项目管理、敏捷开发等内容', (SELECT user_id FROM users WHERE username = 'teacher_li'), 'active');

-- ============================================================
-- 插入知识点数据
-- ============================================================
INSERT INTO `knowledge_points` (`course_id`, `kp_name`, `kp_code`, `difficulty_level`, `description`, `estimated_hours`) VALUES
    -- 数据库系统原理
    (1, '数据库基本概念', 'kp_db_intro', 'basic', '数据库系统、数据模型与数据库管理系统的基本概念', 2.0),
    (1, '关系模型', 'kp_relational_model', 'basic', '关系、元组、属性、键与关系完整性', 3.0),
    (1, 'SQL 基本查询', 'kp_sql_basic', 'basic', 'SELECT、筛选、排序与聚合查询', 4.0),
    (1, '多表连接与子查询', 'kp_sql_join', 'intermediate', '连接查询、嵌套查询与复杂数据检索', 5.0),
    (1, '索引与查询优化', 'kp_index', 'intermediate', 'B+树索引、执行计划与查询优化', 4.0),
    (1, '事务与 ACID', 'kp_transaction', 'intermediate', '事务特性、提交与回滚', 4.0),
    (1, '并发控制与锁', 'kp_concurrency', 'advanced', '隔离级别、并发异常与锁机制', 5.0),
    (1, '范式与反范式', 'kp_norm', 'intermediate', '关系规范化、范式判断与反范式设计', 3.0),
    (1, '数据库设计 (E-R)', 'kp_design', 'intermediate', '概念模型、逻辑模型与物理设计', 4.0),
    -- Python程序设计
    (2, 'Python 语法基础', 'kp_py_syntax', 'basic', '数据类型、运算符与流程控制', 3.0),
    (2, '函数与模块', 'kp_py_func', 'basic', '函数参数、作用域、模块与包', 3.0),
    (2, '面向对象', 'kp_py_oop', 'intermediate', '类、对象、继承与多态', 4.0),
    (2, '异常与测试', 'kp_py_except', 'intermediate', '异常处理、断言与自动化测试', 3.0),
    (2, 'Web 后端基础', 'kp_py_web', 'advanced', 'HTTP、接口开发与数据持久化', 5.0),
    -- 软件工程实践
    (3, '软件过程模型', 'kp_se_process', 'basic', '瀑布、迭代与增量过程', 2.0),
    (3, '需求分析', 'kp_se_req', 'intermediate', '需求获取、建模与规格说明', 4.0),
    (3, '系统设计', 'kp_se_design', 'intermediate', '架构、模块与接口设计', 4.0),
    (3, '敏捷与 Scrum', 'kp_se_agile', 'intermediate', '敏捷价值观、迭代与团队协作', 3.0),
    (3, '测试与质量保障', 'kp_se_test', 'intermediate', '测试策略、质量度量与持续改进', 3.0);

-- ============================================================
-- 插入学习任务数据
-- ============================================================
INSERT INTO `learning_tasks` (`course_id`, `title`, `description`, `target_kp_ids`, `creator_id`, `status`) VALUES
    (1, '数据库事务与并发控制', '学习事务的ACID特性，掌握四种隔离级别的区别和应用场景', '6,7', (SELECT user_id FROM users WHERE username = 'teacher_li'), 'assigned'),
    (1, 'SQL多表连接练习', '完成教务系统多表查询练习，包括INNER JOIN和LEFT JOIN', '4', (SELECT user_id FROM users WHERE username = 'teacher_li'), 'assigned'),
    (2, 'Python函数与模块练习', '编写一个包含多个函数的Python模块，实现基本的文本处理功能', '11', (SELECT user_id FROM users WHERE username = 'teacher_li'), 'assigned'),
    (3, 'UML建模实践', '使用UML工具为选定的系统绘制完整的用例图和类图', '17', (SELECT user_id FROM users WHERE username = 'teacher_li'), 'draft');

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

-- ============================================================
-- A3 补充数据：学生画像、知识点掌握度，学习反馈
-- ============================================================

-- 插入学生画像（student_profiles）
INSERT INTO `student_profiles` (`student_id`, `course_id`, `learning_goal`, `current_level`, `interests`, `resource_preferences`, `weekly_hours`, `mastery_score`) VALUES
    -- 李明：掌握度 42%，薄弱：多表连接、事务隔离级别
    ((SELECT user_id FROM users WHERE username = 'student_zhang'), 1,
     '掌握数据库系统原理，能够独立完成数据库设计、SQL查询优化，能在两周内完成课程 Web 项目',
     '已掌握 SQL 基本查询和数据定义 DDL，多表连接和事务管理薄弱',
     '数据库实践,Web开发,项目实战',
     '案例讲解,图解说明,代码实操',
     8, 0.42),
    -- 王悦：掌握度 68%，薄弱：索引优化、查询计划分析
    ((SELECT user_id FROM users WHERE username = 'student_liu'), 1,
     '深入理解数据库原理，能够进行性能调优和复杂业务数据库设计',
     'SQL 查询基础扎实，理解索引概念，但缺乏实战经验',
     '数据库优化,数据分析',
     '理论讲解,案例对比,实操练习',
     10, 0.68),
    -- 陈思雨：掌握度 35%，薄弱：函数参数传递、模块导入
    ((SELECT user_id FROM users WHERE username = 'student_chen'), 2,
     '掌握 Python 程序设计基础，能独立编写 Web 后端接口',
     '有 C 语言基础，Python 语法入门，函数和模块使用不熟练',
     'Web开发,Python后端',
     '视频教程,代码示例,项目驱动',
     6, 0.35);

-- 插入知识点掌握度（student_knowledge_mastery）
INSERT INTO `student_knowledge_mastery` (`profile_id`, `kp_id`, `mastery_level`, `last_test_score`, `last_test_date`, `update_reason`) VALUES
    -- 李明（profile_id=1）
    (1, 1, 0.80, 0.85, '2026-05-15', '第三次测验准确率 85%'),
    (1, 2, 0.90, 0.92, '2026-05-20', '第四次测验准确率 92%，已熟练掌握'),
    (1, 3, 0.75, 0.78, '2026-05-18', '课堂练习完成较好'),
    (1, 4, 0.30, 0.30, '2026-06-01', '多表连接测验正确率仅 30%，专项训练不足'),
    (1, 6, 0.20, 0.20, '2026-06-01', '从未正确解答事务隔离级别题目'),
    (1, 8, 0.40, 0.40, '2026-05-25', '范式理解停留在概念层面'),
    (1, 5, 0.45, 0.45, '2026-05-28', '索引设计原则有所了解但不会应用'),
    -- 王悦（profile_id=2）
    (2, 1, 0.85, 0.88, '2026-05-10', '基础概念掌握良好'),
    (2, 2, 0.90, 0.95, '2026-05-15', '复杂查询掌握较好'),
    (2, 4, 0.60, 0.65, '2026-06-01', '多表连接基本正确，复杂场景仍有问题'),
    (2, 6, 0.55, 0.55, '2026-05-30', '事务隔离级别理解不深'),
    (2, 8, 0.72, 0.75, '2026-05-20', '范式应用基本正确'),
    (2, 5, 0.30, 0.30, '2026-06-01', '索引优化缺乏实战经验，需要专项练习'),
    -- 陈思雨（profile_id=3）
    (3, 10, 0.75, 0.80, '2026-05-15', '基础语法掌握良好'),
    (3, 11, 0.30, 0.30, '2026-06-01', '函数参数传递混淆不清'),
    (3, 12, 0.25, 0.25, '2026-06-01', '面向对象概念理解不牢'),
    (3, 13, 0.40, 0.40, '2026-05-28', '异常处理概念了解但不会用');

-- 插入学习反馈示例（learning_feedbacks）
INSERT INTO `learning_feedbacks` (`profile_id`, `resource_id`, `course_id`, `feedback_type`, `content`, `quiz_score`, `self_mastery`, `difficulty_rating`) VALUES
    (1, NULL, 1, 'self_report',
     '讲义内容清晰，特别是 INNER JOIN 和 LEFT JOIN 的区别讲得很清楚。案例也很实用，但练习题偏少，希望能增加更多实战练习。',
     NULL, 0.55, 'appropriate'),
    (1, NULL, 1, 'quiz_result',
     '测验有一定难度，对隔离级别理解更深了，但还是会在脏读和不可重复读之间混淆。',
     0.30, NULL, 'too_hard'),
    (2, NULL, 1, 'self_report',
     '索引设计原则讲解透彻，对 B+ 树有了直观理解，但实战案例偏少。',
     NULL, 0.65, 'appropriate');
