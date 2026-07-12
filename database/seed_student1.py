#!/usr/bin/env python3
"""
为 student1 (user_id=2) 插入完整的演示数据。
运行方式: python seed_student1.py
"""

import pymysql
import random
import json
from datetime import datetime, timedelta

DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "061202",
    "database": "ai_collab_audit_system",
    "charset": "utf8mb4",
}

STUDENT_ID = 2   # student1
COURSE_ID  = 1   # 数据库系统原理


def get_conn():
    return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, autocommit=False, **DB)


def insert_profile(conn) -> int:
    cursor = conn.cursor()
    sql = """
    INSERT INTO student_profiles
      (student_id, course_id, learning_goal, current_level, interests,
       resource_preferences, weekly_hours, mastery_score)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        STUDENT_ID, COURSE_ID,
        "系统掌握数据库系统原理，能够独立完成数据库设计、SQL查询与优化，为后继 Web 开发项目打好数据层基础",
        "已学习过 SQL 基本查询语句，了解 SELECT/WHERE/ORDER BY 用法；对多表连接和事务概念零基础",
        "数据库原理,Web后端开发,实战项目",
        "案例讲解,图解动画,配套练习,代码实操",
        10, 0.35
    ))
    conn.commit()
    pid = int(cursor.lastrowid)
    print(f"  ✓ student_profiles inserted, profile_id={pid}")
    return pid


def insert_knowledge_mastery(conn, pid: int):
    cursor = conn.cursor()
    records = [
        # (kp_id, mastery_level, last_test_score, test_date, update_reason)
        (1, 0.85, 0.88, '2026-06-01', '关系模型基础概念清晰，测验准确率 88%'),
        (2, 0.90, 0.92, '2026-06-03', 'SQL 基本查询熟练，掌握子查询与聚合函数'),
        (3, 0.72, 0.75, '2026-06-05', 'DDL 语句基本正确，ALTER TABLE 稍有不熟'),
        (4, 0.28, 0.25, '2026-06-10', '多表连接混淆，LEFT JOIN 和 RIGHT JOIN 语义不清'),
        (5, 0.18, 0.15, '2026-06-12', '事务隔离级别从未正确理解，脏读/不可重复读概念模糊'),
        (6, 0.45, 0.45, '2026-06-08', '范式概念了解，但不会实际判断与规范化'),
        (7, 0.30, 0.30, '2026-06-14', '索引B+树结构不理解，不知道何时建索引'),
        (8, 0.50, 0.52, '2026-06-06', 'ER图画法基本正确，概念模型转逻辑模型薄弱'),
    ]
    sql = """
    INSERT INTO student_knowledge_mastery
      (profile_id, kp_id, mastery_level, last_test_score, last_test_date, update_reason)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    for r in records:
        cursor.execute(sql, (pid, *r))
    conn.commit()
    print(f"  ✓ student_knowledge_mastery {len(records)} records")


def insert_feedback(conn, pid: int):
    cursor = conn.cursor()
    now = datetime.now()
    records = [
        # (resource_id, course_id, feedback_type, content, quiz_score, self_mastery, difficulty_rating, days_ago)
        (None, COURSE_ID, 'self_report',
         '事务隔离级别这章内容很抽象，四种隔离级别看了三遍还是记不住区别。案例里银行转账的脏读例子帮助理解了，但不可重复读和幻读还是有些混淆。',
         None, 0.30, 'too_hard', 7),
        (None, COURSE_ID, 'quiz_result',
         '多表连接练习题得分偏低，INNER JOIN 基本正确，LEFT JOIN 漏掉了右表为 NULL 的情况，RIGHT JOIN 完全不会。',
         0.28, None, 'too_hard', 5),
        (None, COURSE_ID, 'self_report',
         'ER 图绘制练习完成较好，对实体、属性、联系的区分清晰了。数据库设计第三范式还有点模糊，需要再找练习题巩固。',
         None, 0.55, 'appropriate', 3),
        (None, COURSE_ID, 'quiz_result',
         '索引与优化章节测验，只有 B+ 树高度计算做对了，索引设计原则几乎全错，不知道什么字段适合建索引。',
         0.30, None, 'too_hard', 1),
    ]
    sql = """
    INSERT INTO learning_feedbacks
      (profile_id, resource_id, course_id, feedback_type, content,
       quiz_score, self_mastery, difficulty_rating, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for resource_id, course_id, feedback_type, content, quiz_score, self_mastery, difficulty, days_ago in records:
        created_at = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(sql, (pid, resource_id, course_id, feedback_type, content,
                             quiz_score, self_mastery, difficulty, created_at))
    conn.commit()
    print(f"  ✓ learning_feedbacks {len(records)} records")


def insert_tutor_sessions(conn, pid: int):
    cursor = conn.cursor()
    now = datetime.now()
    sessions = [
        # (question, answer, explanation_level, helpful, days_ago, hours_offset)
        ('可重复读和串行化到底有什么区别？我总是混淆这两个隔离级别。',
         '可重复读（Repeatable Read）和串行化（Serializable）的主要区别在于并发控制粒度。可重复读使用 MVCC 快照读，允许不可重复读但不允许脏读；串行化则强制事务串行执行，完全禁止并发冲突，但性能最差。简单记法：读已提交（Read Committed）解决脏读；可重复读（Repeatable Read）解决不可重复读；串行化（Serializable）解决幻读。',
         'intermediate', 1, 6, 10),
        ('多表连接什么时候应该使用 LEFT JOIN？',
         'LEFT JOIN（又称 LEFT OUTER JOIN）用于保留左表的全部记录，当右表没有匹配时显示 NULL。适用场景：1）需要左表所有记录，即使右表没有关联；2）查找左表中在右表没有对应记录的"孤儿"数据；3）替代 NOT IN / NOT EXISTS 子查询。示例：SELECT s.name, g.grade FROM students s LEFT JOIN grades g ON s.id=g.student_id，可以列出所有学生，包括没有成绩的。',
         'basic', 1, 4, 14),
        ('事务隔离级别和锁机制有什么关系？',
         '隔离级别通过不同的锁策略来实现：读已提交（RC）通常使用语句级快照；可重复读（RR）使用事务级快照；而串行化则通过间隙锁（Gap Lock）和谓词锁阻止幻读。锁的粒度可以是行锁、表锁、页锁，MySQL InnoDB 的行锁实际上是索引记录锁，所以没有索引的查询会锁住整张表。',
         'advanced', None, 2, 16),
        ('B+ 树索引为什么比哈希索引更适合范围查询？',
         'B+ 树索引的叶子节点通过双向指针有序连接，适合范围查询（>, <, BETWEEN）；而哈希索引基于哈希表，只能做等值查询（=, IN），无法进行范围扫描。另外，B+ 树索引支持最左前缀匹配原则，对字符串前缀匹配也很高效。哈希索引适合等值查询极快的场景，但不适合排序和范围查询。',
         'intermediate', 1, 1, 9),
    ]
    sql = """
    INSERT INTO tutor_sessions
      (profile_id, course_id, question, answer, explanation_level, helpful, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for question, answer, level, helpful, days_ago, hour_offset in sessions:
        created_at = (now - timedelta(days=days_ago, hours=hour_offset)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(sql, (pid, COURSE_ID, question, answer, level, helpful, created_at))
    conn.commit()
    print(f"  ✓ tutor_sessions {len(sessions)} sessions")


def insert_profile_update_history(conn, pid: int):
    cursor = conn.cursor()
    now = datetime.now()
    history = [
        # (update_type, before_json, after_json, change_summary, days_ago)
        ('quiz_result',
         json.dumps({"mastery_score": 0.30, "kp_5": 0.18}, ensure_ascii=False),
         json.dumps({"mastery_score": 0.35, "kp_5": 0.18}, ensure_ascii=False),
         '综合掌握度由 30% 更新为 35%，事务隔离级别掌握度维持 18%',
         7),
        ('dialog',
         json.dumps({"mastery_score": 0.35, "kp_5": 0.18}, ensure_ascii=False),
         json.dumps({"mastery_score": 0.32, "kp_4": 0.28}, ensure_ascii=False),
         'AI 辅导后多表连接知识点掌握度从 0 更新为 28%，综合分略降',
         4),
        ('self_report',
         json.dumps({"mastery_score": 0.32, "kp_4": 0.28}, ensure_ascii=False),
         json.dumps({"mastery_score": 0.35, "interests": "数据库原理,Web后端开发"}, ensure_ascii=False),
         '学生自评 ER 图绘制较好，兴趣更新为数据库原理与 Web 后端开发',
         2),
    ]
    sql = """
    INSERT INTO profile_update_history
      (profile_id, update_type, before_json, after_json, change_summary, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    for update_type, before, after, summary, days_ago in history:
        created_at = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(sql, (pid, update_type, before, after, summary, created_at))
    conn.commit()
    print(f"  ✓ profile_update_history {len(history)} records")


def insert_ai_invocations(conn, pid: int):
    """
    插入近14天 AI 调用记录（用于统计概览页的调用趋势图）。
    ai_invocations 表通过 project_id/task_id 关联，不直接关联 profile_id，
    因此这里用 student 自己的 project（project_id=2）来记录，便于区分归属。
    """
    cursor = conn.cursor()
    now = datetime.now()
    rng = random.Random(42)
    # 每天的调用量（固定种子保证可重复）
    daily_counts = [3, 5, 2, 7, 4, 6, 1, 5, 8, 3, 4, 6, 2, 5]
    records = []
    for day_idx, count in enumerate(daily_counts):
        base_date = now - timedelta(days=13 - day_idx)
        for _ in range(count):
            h = rng.randint(8, 22)
            m = rng.randint(0, 59)
            s = rng.randint(0, 59)
            created_at = (base_date.replace(hour=h, minute=m, second=s)).strftime('%Y-%m-%d %H:%M:%S')
            records.append((
                2, None, None, 1, 1,
                f"SELECT * FROM students WHERE id={pid}",  # input_text 占位
                f"Mock response for student {pid}",         # output_text 占位
                rng.randint(100, 500), rng.randint(100, 300), rng.randint(100, 800),
                'success', created_at
            ))
    sql = """
    INSERT INTO ai_invocations
      (project_id, task_id, branch_id, model_id, prompt_version_id,
       input_text, output_text, input_tokens, output_tokens, latency_ms,
       status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, records)
    conn.commit()
    print(f"  ✓ ai_invocations {len(records)} records (mock, for statistics)")


def assign_tasks(conn):
    """将学习任务指派给 student1"""
    cursor = conn.cursor()
    now = datetime.now()
    tasks = [
        # (task_id, status, due_days)
        (1, 'in_progress', 7),
        (2, 'assigned',   14),
    ]
    for task_id, status, due_days in tasks:
        due = (now + timedelta(days=due_days)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "UPDATE learning_tasks SET assignee_id=%s, status=%s, due_date=%s WHERE task_id=%s",
            (STUDENT_ID, status, due, task_id)
        )
    conn.commit()
    print(f"  ✓ learning_tasks assigned {len(tasks)} tasks to student1")


def main():
    print("\n=== 为 student1 插入完整演示数据 ===\n")
    conn = get_conn()
    try:
        pid = insert_profile(conn)
        insert_knowledge_mastery(conn, pid)
        insert_feedback(conn, pid)
        insert_tutor_sessions(conn, pid)
        insert_profile_update_history(conn, pid)
        insert_ai_invocations(conn, pid)
        assign_tasks(conn)
        print(f"\n✅ 全部完成！")
        print(f"   student1 (user_id={STUDENT_ID})")
        print(f"   profile_id={pid}, course_id={COURSE_ID}")
        print(f"   登录密码: student1123456")
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
