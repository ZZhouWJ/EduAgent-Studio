"""
Seed demo data for EduAgent Studio.

What it does
------------
- Inserts 1 admin, 2 teachers, 6 students (with bcrypt-hashed `Pass@1234`).
- Ensures teacher / student roles are assigned.
- Ensures 3 courses exist and are owned by the right teachers.
- Seeds knowledge points, student profiles, learning mastery, projects,
  project members, project tasks, task branches, task outputs,
  review requests, output reviews, learning resources, learning tasks,
  learning feedbacks, model providers, AI models, API configs,
  AI invocations, cost records, and a few operation/login logs.
- Idempotent: re-runnable. Existing rows are updated, not duplicated,
  so you can run it multiple times safely.

How to run
----------
    cd backend
    .venv/bin/python database/seed_demo_data.py

Prereqs
-------
- .env configured (DB_HOST/DB_USER/DB_PASSWORD/DB_NAME point to MySQL).
- MySQL is reachable, the 39 tables already exist (created by the app).
- The bcrypt package is installed in the venv.
"""

from __future__ import annotations

import logging
import os
import random
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Tuple

import bcrypt
import pymysql
from pymysql.cursors import DictCursor

# ---------------------------------------------------------------------------
# Bootstrap Django-less settings: read .env manually.
# ---------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATHS = (
    os.path.join(BASE_DIR, ".env"),
    os.path.join(BASE_DIR, "backend", ".env"),
)


def _load_env() -> Dict[str, str]:
    env: Dict[str, str] = {}
    for env_path in ENV_PATHS:
        if not os.path.exists(env_path):
            continue
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    env.update({key: value for key, value in os.environ.items() if key.startswith("DB_")})
    return env


ENV = _load_env()
DB_CFG = {
    "host": ENV.get("DB_HOST", "127.0.0.1"),
    "port": int(ENV.get("DB_PORT", "3306")),
    "user": ENV.get("DB_USER", "root"),
    "password": ENV.get("DB_PASSWORD", ""),
    "database": ENV.get("DB_NAME", "ai_collab_audit_system"),
    "charset": "utf8mb4",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("seed")


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------


def connect() -> pymysql.connections.Connection:
    log.info("Connecting to MySQL %s@%s/%s", DB_CFG["user"], DB_CFG["host"], DB_CFG["database"])
    return pymysql.connect(**DB_CFG, autocommit=False, cursorclass=DictCursor)


def fetchone(cur, sql: str, *args) -> Optional[Dict[str, Any]]:
    cur.execute(sql, args or ())
    return cur.fetchone()


def fetchall(cur, sql: str, *args) -> List[Dict[str, Any]]:
    cur.execute(sql, args or ())
    return list(cur.fetchall())


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


# ---------------------------------------------------------------------------
# People & roles
# ---------------------------------------------------------------------------

DEMO_PASSWORD = "Pass@1234"
DEMO_PWHASH = hash_password(DEMO_PASSWORD)


# (username, real_name, email, student_no, phone, role_codes)
DEMO_USERS: List[Tuple[str, str, str, Optional[str], str, List[str]]] = [
    # admin
    ("admin", "系统管理员", "admin@eduagent.local", None, "13800000001", ["admin"]),
    # teachers
    ("teacher_li", "李建国", "li.jianguo@eduagent.local", None, "13800000010", ["teacher"]),
    ("teacher_wang", "王雪", "wang.xue@eduagent.local", None, "13800000011", ["teacher"]),
    # students
    ("student_zhang", "张小明", "zhang.xm@eduagent.local", "2024001001", "13800000201", ["student_member"]),
    ("student_liu", "刘洋", "liu.yang@eduagent.local", "2024001002", "13800000202", ["student_member"]),
    ("student_chen", "陈雨欣", "chen.yx@eduagent.local", "2024001003", "13800000203", ["student_member"]),
    ("student_zhao", "赵伟", "zhao.wei@eduagent.local", "2024001004", "13800000204", ["student_member"]),
    ("student_sun", "孙佳", "sun.jia@eduagent.local", "2024001005", "13800000205", ["student_member"]),
    ("student_zhou", "周琪", "zhou.qi@eduagent.local", "2024001006", "13800000206", ["student_member"]),
]


def upsert_user(cur, username: str, real_name: str, email: Optional[str],
                student_no: Optional[str], phone: str) -> int:
    row = fetchone(cur, "SELECT user_id FROM users WHERE username=%s", username)
    if row:
        uid = row["user_id"]
        cur.execute(
            """UPDATE users SET password_hash=%s, real_name=%s, email=%s, student_no=%s, phone=%s,
                                 status='active', is_deleted=0
               WHERE user_id=%s""",
            (DEMO_PWHASH, real_name, email, student_no, phone, uid),
        )
        return uid
    cur.execute(
        """INSERT INTO users (username, password_hash, real_name, student_no,
                              email, phone, status, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, 'active', 0)""",
        (username, DEMO_PWHASH, real_name, student_no, email, phone),
    )
    return cur.lastrowid


def assign_role(cur, user_id: int, role_code: str) -> None:
    role = fetchone(cur, "SELECT role_id FROM roles WHERE role_code=%s AND is_deleted=0", role_code)
    if not role:
        log.warning("role %s not found, skipping", role_code)
        return
    rid = role["role_id"]
    existing = fetchone(
        cur,
        "SELECT user_role_id FROM user_roles WHERE user_id=%s AND role_id=%s AND is_deleted=0",
        user_id, rid,
    )
    if existing:
        return
    cur.execute(
        """INSERT INTO user_roles (user_id, role_id, is_deleted)
           VALUES (%s, %s, 0)""",
        (user_id, rid),
    )


# ---------------------------------------------------------------------------
# Courses & knowledge points
# ---------------------------------------------------------------------------

COURSES: List[Tuple[str, str, str, str]] = [
    # (course_code, course_name, description, owner_username)
    ("CS301", "数据库系统原理",
     "系统学习数据库系统的基本概念、关系模型、SQL语言、事务与并发控制、数据库设计等内容",
     "teacher_li"),
    ("CS201", "Python 程序设计",
     "Python 编程语言基础、函数、模块、面向对象、异常处理以及 Web 后端开发",
     "teacher_wang"),
    ("CS401", "软件工程实践",
     "软件工程方法论、需求分析、系统设计、项目管理、敏捷开发与持续集成",
     "teacher_wang"),
]


def upsert_course(cur, code: str, name: str, desc: str, teacher_id: int) -> int:
    row = fetchone(cur, "SELECT course_id FROM courses WHERE course_code=%s AND is_deleted=0", code)
    if row:
        cid = row["course_id"]
        cur.execute(
            "UPDATE courses SET course_name=%s, description=%s, teacher_id=%s, status='active' WHERE course_id=%s",
            (name, desc, teacher_id, cid),
        )
        return cid
    cur.execute(
        """INSERT INTO courses (course_code, course_name, description, teacher_id, status, is_deleted)
           VALUES (%s, %s, %s, %s, 'active', 0)""",
        (code, name, desc, teacher_id),
    )
    return cur.lastrowid


KNOWLEDGE_POINTS: Dict[str, List[Tuple[str, str, str, float]]] = {
    "CS301": [
        ("kp_db_intro", "数据库基本概念", "basic", 2.0),
        ("kp_relational_model", "关系模型", "basic", 3.0),
        ("kp_sql_basic", "SQL 基本查询", "basic", 4.0),
        ("kp_sql_join", "多表连接与子查询", "intermediate", 5.0),
        ("kp_index", "索引与查询优化", "intermediate", 4.0),
        ("kp_transaction", "事务与 ACID", "intermediate", 4.0),
        ("kp_concurrency", "并发控制与锁", "advanced", 5.0),
        ("kp_norm", "范式与反范式", "intermediate", 3.0),
        ("kp_design", "数据库设计 (E-R)", "intermediate", 4.0),
    ],
    "CS201": [
        ("kp_py_syntax", "Python 语法基础", "basic", 3.0),
        ("kp_py_func", "函数与模块", "basic", 3.0),
        ("kp_py_oop", "面向对象", "intermediate", 4.0),
        ("kp_py_except", "异常与测试", "intermediate", 3.0),
        ("kp_py_web", "Web 后端基础", "advanced", 5.0),
    ],
    "CS401": [
        ("kp_se_process", "软件过程模型", "basic", 2.0),
        ("kp_se_req", "需求分析", "intermediate", 4.0),
        ("kp_se_design", "系统设计", "intermediate", 4.0),
        ("kp_se_agile", "敏捷与 Scrum", "intermediate", 3.0),
        ("kp_se_test", "测试与质量保障", "intermediate", 3.0),
    ],
}


def upsert_kp(cur, course_id: int, code: str, name: str, difficulty: str, hours: float) -> int:
    row = fetchone(
        cur,
        "SELECT kp_id FROM knowledge_points WHERE course_id=%s AND kp_code=%s",
        course_id, code,
    )
    if row:
        return row["kp_id"]
    cur.execute(
        """INSERT INTO knowledge_points
               (course_id, kp_name, kp_code, difficulty_level, estimated_hours, is_deleted)
           VALUES (%s, %s, %s, %s, %s, 0)""",
        (course_id, name, code, difficulty, hours),
    )
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Student profiles & mastery
# ---------------------------------------------------------------------------

STUDENT_PROFILES: List[Tuple[str, str, str, str, str, int, float]] = [
    # (username, course_code, learning_goal, current_level, interests, weekly_hours, mastery_score)
    ("student_zhang", "CS301",
     "掌握数据库系统原理，能够独立完成数据库设计、SQL查询优化，能在两周内完成课程 Web 项目",
     "已掌握 SQL 基本查询和数据定义 DDL，多表连接和事务管理薄弱",
     "数据库实践,Web开发,项目实战", 8, 0.42),
    ("student_liu", "CS301",
     "深入理解数据库原理，能够进行性能调优和复杂业务数据库设计",
     "SQL 查询基础扎实，理解索引概念，但缺乏实战经验",
     "数据库优化,数据分析", 10, 0.68),
    ("student_chen", "CS201",
     "掌握 Python 程序设计基础，能独立编写 Web 后端接口",
     "有 C 语言基础，Python 语法入门，函数和模块使用不熟练",
     "Web开发,Python后端", 6, 0.35),
    ("student_zhao", "CS201",
     "能用 Python 完成数据处理与可视化任务",
     "Python 基础扎实，正在学习数据科学方向",
     "数据分析,可视化", 9, 0.72),
    ("student_sun", "CS401",
     "理解软件工程全流程，能在团队中担任前端或测试角色",
     "熟悉基础开发，缺少工程化经验",
     "前端开发,UI设计", 7, 0.50),
    ("student_zhou", "CS401",
     "成为全栈工程师，掌握需求→设计→实现→测试全链路",
     "后端基础扎实，前端能力薄弱",
     "后端开发,系统设计", 10, 0.61),
]


def upsert_student_profile(cur, student_id: int, course_id: int, goal: str, level: str,
                            interests: str, weekly_hours: int, mastery: float) -> int:
    row = fetchone(
        cur,
        "SELECT profile_id FROM student_profiles WHERE student_id=%s AND course_id=%s",
        student_id, course_id,
    )
    if row:
        pid = row["profile_id"]
        cur.execute(
            """UPDATE student_profiles SET learning_goal=%s, current_level=%s, interests=%s,
                                           resource_preferences='案例讲解,图解说明,代码实操',
                                           weekly_hours=%s, mastery_score=%s, is_deleted=0
               WHERE profile_id=%s""",
            (goal, level, interests, weekly_hours, mastery, pid),
        )
        return pid
    cur.execute(
        """INSERT INTO student_profiles
               (student_id, course_id, learning_goal, current_level, interests,
                resource_preferences, weekly_hours, mastery_score, is_deleted)
           VALUES (%s, %s, %s, %s, %s, '案例讲解,图解说明,代码实操', %s, %s, 0)""",
        (student_id, course_id, goal, level, interests, weekly_hours, mastery),
    )
    return cur.lastrowid


def seed_mastery(cur, profile_id: int, kp_ids: List[int], base: float) -> None:
    """Fill per-KP mastery around `base` with noise; skips if row exists."""
    random.seed(profile_id)
    for kp_id in kp_ids:
        score = max(0.05, min(0.95, base + random.uniform(-0.20, 0.25)))
        row = fetchone(
            cur,
            "SELECT mastery_id FROM student_knowledge_mastery WHERE profile_id=%s AND kp_id=%s",
            profile_id, kp_id,
        )
        if row:
            cur.execute(
                """UPDATE student_knowledge_mastery SET mastery_level=%s, last_test_score=%s,
                                                       last_test_date=%s, update_reason=%s
                   WHERE mastery_id=%s""",
                (round(score, 3), round(score + random.uniform(-0.05, 0.1), 3),
                 date.today() - timedelta(days=random.randint(1, 14)),
                 "系统根据近期测验自动更新", row["mastery_id"]),
            )
        else:
            cur.execute(
                """INSERT INTO student_knowledge_mastery
                       (profile_id, kp_id, mastery_level, last_test_score,
                        last_test_date, update_reason, is_deleted)
                   VALUES (%s, %s, %s, %s, %s, '系统根据近期测验自动更新', 0)""",
                (profile_id, kp_id, round(score, 3),
                 round(score + random.uniform(-0.05, 0.1), 3),
                 date.today() - timedelta(days=random.randint(1, 14))),
            )


# ---------------------------------------------------------------------------
# Model providers, AI models, API configs
# ---------------------------------------------------------------------------


def upsert_provider(cur, name: str, code: str, base_url: str, website: str, desc: str) -> int:
    row = fetchone(cur, "SELECT provider_id FROM model_providers WHERE provider_code=%s", code)
    if row:
        return row["provider_id"]
    cur.execute(
        """INSERT INTO model_providers (provider_name, provider_code, base_url, website, description, status, is_deleted)
           VALUES (%s, %s, %s, %s, %s, 'active', 0)""",
        (name, code, base_url, website, desc),
    )
    return cur.lastrowid


def upsert_ai_model(cur, provider_id: int, model_name: str, display_name: str,
                    input_price: float, output_price: float,
                    capability_tags: str, max_context: int) -> int:
    row = fetchone(
        cur,
        "SELECT model_id FROM ai_models WHERE provider_id=%s AND model_name=%s",
        provider_id, model_name,
    )
    if row:
        mid = row["model_id"]
        cur.execute(
            """UPDATE ai_models SET display_name=%s, input_price=%s, output_price=%s,
                                     capability_tags=%s, max_context=%s, status='active'
               WHERE model_id=%s""",
            (display_name, input_price, output_price, capability_tags, max_context, mid),
        )
        return mid
    cur.execute(
        """INSERT INTO ai_models
               (provider_id, model_name, display_name, capability_tags, max_context,
                input_price, output_price, price_unit, status, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, '1K_TOKENS', 'active', 0)""",
        (provider_id, model_name, display_name, capability_tags, max_context,
         input_price, output_price),
    )
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Projects, tasks, branches, outputs
# ---------------------------------------------------------------------------

PROJECTS: List[Tuple[str, str, str, str, List[str]]] = [
    # (project_name, project_type, description, owner_username, member_usernames)
    ("数据库课程综合实践 - 校园选课系统",
     "课程项目",
     "完成一个基于 MySQL + FastAPI 的校园选课系统后端，覆盖事务、索引、并发等核心知识点",
     "teacher_li",
     ["student_zhang", "student_liu"]),
    ("Python Web 数据看板",
     "兴趣项目",
     "基于 Flask + ECharts 的数据可视化看板",
     "teacher_wang",
     ["student_chen", "student_zhao"]),
    ("软件工程 - 团队协作流程演练",
     "教学项目",
     "按 Scrum 流程完成一个小型 Web 应用的迭代开发",
     "teacher_wang",
     ["student_sun", "student_zhou"]),
]


TASK_TYPES = [
    ("lecture", "课程讲义生成"),
    ("quiz", "练习题生成"),
    ("case", "案例分析"),
    ("review", "内容审核"),
    ("summary", "知识总结"),
]


def upsert_task_type(cur, code: str, name: str, desc: str) -> int:
    row = fetchone(cur, "SELECT task_type_id FROM task_types WHERE type_code=%s", code)
    if row:
        return row["task_type_id"]
    cur.execute(
        """INSERT INTO task_types (type_name, type_code, description, status, is_deleted)
           VALUES (%s, %s, %s, 'active', 0)""",
        (name, code, desc),
    )
    return cur.lastrowid


def upsert_project(cur, name: str, ptype: str, desc: str, owner_id: int) -> int:
    row = fetchone(cur, "SELECT project_id FROM projects WHERE project_name=%s", name)
    if row:
        return row["project_id"]
    cur.execute(
        """INSERT INTO projects (project_name, project_type, description, owner_id, status, is_deleted)
           VALUES (%s, %s, %s, %s, 'active', 0)""",
        (name, ptype, desc, owner_id),
    )
    return cur.lastrowid


def upsert_project_member(cur, project_id: int, user_id: int, role: str, contribution: float) -> None:
    row = fetchone(
        cur,
        "SELECT member_id FROM project_members WHERE project_id=%s AND user_id=%s",
        project_id, user_id,
    )
    if row:
        cur.execute(
            "UPDATE project_members SET project_role=%s, contribution_score=%s, status='active' WHERE member_id=%s",
            (role, contribution, row["member_id"]),
        )
        return
    cur.execute(
        """INSERT INTO project_members (project_id, user_id, project_role, status, contribution_score, is_deleted)
           VALUES (%s, %s, %s, 'active', %s, 0)""",
        (project_id, user_id, role, contribution),
    )


def upsert_project_task(cur, project_id: int, task_type_id: int, title: str, desc: str,
                         creator_id: int, assignee_id: Optional[int], status: str,
                         priority: str, due_offset_days: int) -> int:
    row = fetchone(
        cur,
        "SELECT task_id FROM project_tasks WHERE project_id=%s AND title=%s",
        project_id, title,
    )
    due = datetime.now() + timedelta(days=due_offset_days)
    if row:
        tid = row["task_id"]
        cur.execute(
            """UPDATE project_tasks SET task_type_id=%s, description=%s, assignee_id=%s,
                                         status=%s, priority=%s, due_date=%s
               WHERE task_id=%s""",
            (task_type_id, desc, assignee_id, status, priority, due, tid),
        )
        return tid
    cur.execute(
        """INSERT INTO project_tasks
               (project_id, task_type_id, title, description, creator_id, assignee_id,
                status, priority, due_date, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)""",
        (project_id, task_type_id, title, desc, creator_id, assignee_id,
         status, priority, due),
    )
    return cur.lastrowid


def upsert_branch(cur, project_id: int, task_id: int, name: str) -> int:
    row = fetchone(
        cur,
        "SELECT branch_id FROM task_branches WHERE task_id=%s AND branch_name=%s",
        task_id, name,
    )
    if row:
        return row["branch_id"]
    cur.execute(
        """INSERT INTO task_branches (project_id, task_id, branch_name, status, is_deleted)
           VALUES (%s, %s, %s, 'active', 0)""",
        (project_id, task_id, name),
    )
    return cur.lastrowid


def upsert_invocation(cur, project_id: int, task_id: int, branch_id: int, model_id: int,
                      prompt_version_id: Optional[int], input_text: str, output_text: str,
                      input_tokens: int, output_tokens: int, latency_ms: int,
                      cost: float, status: str, created_by: int) -> int:
    cur.execute(
        """INSERT INTO ai_invocations
               (project_id, task_id, branch_id, model_id, prompt_version_id,
                input_text, output_text, input_tokens, output_tokens, latency_ms,
                status, cost, created_by, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)""",
        (project_id, task_id, branch_id, model_id, prompt_version_id,
         input_text, output_text, input_tokens, output_tokens, latency_ms,
         status, cost, created_by),
    )
    return cur.lastrowid


def upsert_cost_record(cur, invocation_id: int, project_id: int, task_id: int,
                        model_id: int, user_id: int,
                        input_tokens: int, output_tokens: int,
                        input_cost: float, output_cost: float) -> None:
    cur.execute(
        """INSERT INTO cost_records
               (invocation_id, project_id, task_id, model_id, user_id,
                input_tokens, output_tokens, total_tokens,
                input_cost, output_cost, total_cost, currency)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'CNY')""",
        (invocation_id, project_id, task_id, model_id, user_id,
         input_tokens, output_tokens, input_tokens + output_tokens,
         input_cost, output_cost, input_cost + output_cost),
    )


def upsert_output(cur, task_id: int, branch_id: int, invocation_id: int, title: str,
                   content: str, source_type: str, status: str, created_by: int,
                   is_final: bool = False, version_no: int = 1) -> int:
    cur.execute(
        """INSERT INTO task_outputs
               (task_id, branch_id, invocation_id, version_no, output_title, content,
                source_type, is_final_candidate, status, last_modified_at, created_by, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, 0)""",
        (task_id, branch_id, invocation_id, version_no, title, content,
         source_type, 1 if is_final else 0, status, created_by),
    )
    return cur.lastrowid


def upsert_review_request(cur, output_id: int, task_id: int, project_id: int,
                           submitter_id: int, reviewer_id: Optional[int],
                           status: str, note: str) -> int:
    cur.execute(
        """INSERT INTO review_requests
               (output_id, task_id, project_id, submitter_id, reviewer_id,
                request_status, submit_note, reviewed_at, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s,
                       CASE WHEN %s IN ('pending') THEN NULL ELSE NOW() END,
                       0)""",
        (output_id, task_id, project_id, submitter_id, reviewer_id,
         status, note, status),
    )
    return cur.lastrowid


def upsert_review(cur, request_id: int, output_id: int, reviewer_id: int,
                   accuracy: float, completeness: float, logic: float,
                   format_: float, usability: float, risk: float,
                   status: str, comment: str) -> None:
    cur.execute(
        """INSERT INTO output_reviews
               (request_id, output_id, reviewer_id,
                accuracy_score, completeness_score, logic_score, format_score,
                usability_score, risk_score, review_status, review_comment, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)""",
        (request_id, output_id, reviewer_id, accuracy, completeness, logic, format_,
         usability, risk, status, comment),
    )


def upsert_learning_resource(cur, course_id: int, title: str, rtype: str,
                              difficulty: str, content: str, kp_ids_csv: str,
                              model: str, status: str, created_by: int) -> int:
    row = fetchone(
        cur,
        "SELECT resource_id FROM learning_resources WHERE course_id=%s AND resource_title=%s",
        course_id, title,
    )
    if row:
        rid = row["resource_id"]
        cur.execute(
            """UPDATE learning_resources SET resource_type=%s, difficulty=%s, content=%s,
                                            target_kp_ids=%s, generation_model=%s,
                                            status=%s, is_deleted=0
               WHERE resource_id=%s""",
            (rtype, difficulty, content, kp_ids_csv, model, status, rid),
        )
        return rid
    cur.execute(
        """INSERT INTO learning_resources
               (course_id, resource_title, resource_type, difficulty, content,
                target_kp_ids, generation_model, generation_agent, status, is_deleted, created_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, 'multi_agent_workflow', %s, 0, %s)""",
        (course_id, title, rtype, difficulty, content, kp_ids_csv, model, status, created_by),
    )
    return cur.lastrowid


def upsert_feedback(cur, profile_id: int, course_id: int, resource_id: Optional[int],
                     ftype: str, content: str, score: Optional[float],
                     self_mastery: Optional[float], difficulty: str) -> int:
    cur.execute(
        """INSERT INTO learning_feedbacks
               (profile_id, resource_id, course_id, feedback_type, content,
                quiz_score, self_mastery, difficulty_rating, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)""",
        (profile_id, resource_id, course_id, ftype, content, score, self_mastery, difficulty),
    )
    return cur.lastrowid


def log_operation(cur, user_id: int, project_id: Optional[int], task_id: Optional[int],
                  target_type: Optional[str], target_id: Optional[int], action: str,
                  desc: str) -> None:
    cur.execute(
        """INSERT INTO operation_logs
               (user_id, project_id, task_id, target_type, target_id,
                action_type, action_desc, ip_address, user_agent)
           VALUES (%s, %s, %s, %s, %s, %s, %s, '127.0.0.1', 'seed-script/1.0')""",
        (user_id, project_id, task_id, target_type, target_id, action, desc),
    )


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def get_user_id(cur, username: str) -> int:
    row = fetchone(cur, "SELECT user_id FROM users WHERE username=%s", username)
    if not row:
        raise RuntimeError(f"user {username} not found")
    return row["user_id"]


def get_course_id(cur, code: str) -> int:
    row = fetchone(cur, "SELECT course_id FROM courses WHERE course_code=%s AND is_deleted=0", code)
    if not row:
        raise RuntimeError(f"course {code} not found")
    return row["course_id"]


def main() -> int:
    conn = connect()
    try:
        with conn.cursor() as cur:
            # 0) Clean up any leftover rows from previous failed runs so that
            #    "user_id" stays stable across re-runs. We only touch our own
            #    demo usernames — never the original `admin`, `student1`, etc.
            demo_usernames = [u[0] for u in DEMO_USERS]
            log.info("=== cleanup previous demo rows (idempotent) ===")
            placeholders = ",".join(["%s"] * len(demo_usernames))

            # We only ever delete data we previously inserted, and our cleanup
            # is bounded by the demo usernames / owner_id list, so disabling FK
            # checks is safe and avoids the chore of manually ordering
            # parent/child deletions across 30+ tables.
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")

            # Tables where the user is referenced via a direct FK column.
            USER_COL = [
                ("adopted_outputs", "adopted_by"),
                ("merge_records", "merged_by"),
                ("output_reviews", "reviewer_id"),
                ("review_requests", "submitter_id"),
                ("task_branches", "created_by"),
                ("task_outputs", "created_by"),
                ("ai_invocations", "created_by"),
                ("cost_records", "user_id"),
                ("learning_resources", "created_by"),
                ("project_tasks", "creator_id"),
                ("project_members", "user_id"),
                ("operation_logs", "user_id"),
                ("user_roles", "user_id"),
            ]
            for tbl, col in USER_COL:
                cur.execute(
                    f"DELETE {tbl} FROM {tbl} "
                    f"INNER JOIN users u ON {tbl}.{col} = u.user_id "
                    f"WHERE u.username IN ({placeholders})",
                    demo_usernames,
                )

            # Tables linked through `student_profiles`. Deleting the profile
            # also drops the dependent mastery/feedback rows.
            cur.execute(
                f"DELETE sp, skm, lf FROM student_profiles sp "
                f"INNER JOIN users u ON sp.student_id = u.user_id "
                f"LEFT JOIN student_knowledge_mastery skm ON skm.profile_id = sp.profile_id "
                f"LEFT JOIN learning_feedbacks lf ON lf.profile_id = sp.profile_id "
                f"WHERE u.username IN ({placeholders})",
                demo_usernames,
            )

            # learning_tasks is assigned to students (assignee_id), not a teacher.
            cur.execute(
                f"DELETE FROM learning_tasks WHERE assignee_id IN "
                f"(SELECT user_id FROM users WHERE username IN ({placeholders}))",
                demo_usernames,
            )
            # project_tasks.assignee_id can also be a student; we already
            # deleted by creator_id above, but the assignee may still hold FK.
            cur.execute(
                f"DELETE FROM project_tasks WHERE assignee_id IN "
                f"(SELECT user_id FROM users WHERE username IN ({placeholders}))",
                demo_usernames,
            )

            # login_logs has username column instead of user_id.
            cur.execute(
                f"DELETE FROM login_logs WHERE username IN ({placeholders})",
                demo_usernames,
            )
            # projects owned by demo teachers.
            cur.execute(
                f"DELETE FROM projects WHERE owner_id IN "
                f"(SELECT user_id FROM users WHERE username IN ({placeholders}))",
                demo_usernames,
            )
            # Finally the users themselves.
            cur.execute(
                f"DELETE FROM users WHERE username IN ({placeholders})",
                demo_usernames,
            )

            # Re-enable FK checks now that demo rows are gone.
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            log.info("  cleanup done")

            log.info("=== users & roles ===")
            for username, real_name, email, student_no, phone, roles in DEMO_USERS:
                uid = upsert_user(cur, username, real_name, email, student_no, phone)
                # Always reset password to the demo password so re-runs stay usable.
                cur.execute(
                    "UPDATE users SET password_hash=%s WHERE user_id=%s",
                    (DEMO_PWHASH, uid),
                )
                for rc in roles:
                    assign_role(cur, uid, rc)
                log.info("  user %s (id=%s) -> roles %s", username, uid, roles)

            log.info("=== courses ===")
            course_ids: Dict[str, int] = {}
            for code, name, desc, owner_username in COURSES:
                owner_id = get_user_id(cur, owner_username)
                cid = upsert_course(cur, code, name, desc, owner_id)
                course_ids[code] = cid
                log.info("  course %s (id=%s) owner=%s", code, cid, owner_username)

            log.info("=== knowledge points ===")
            kp_ids_by_course: Dict[int, List[int]] = {}
            for code, kps in KNOWLEDGE_POINTS.items():
                cid = course_ids[code]
                ids = []
                for kcode, kname, diff, hours in kps:
                    kid = upsert_kp(cur, cid, kcode, kname, diff, hours)
                    ids.append(kid)
                kp_ids_by_course[cid] = ids
                log.info("  %s: %d knowledge points", code, len(ids))

            log.info("=== student profiles + mastery ===")
            profile_ids: Dict[Tuple[str, str], int] = {}
            for username, code, goal, level, interests, weekly, mastery in STUDENT_PROFILES:
                student_id = get_user_id(cur, username)
                cid = course_ids[code]
                pid = upsert_student_profile(cur, student_id, cid, goal, level,
                                              interests, weekly, mastery)
                profile_ids[(username, code)] = pid
                seed_mastery(cur, pid, kp_ids_by_course[cid], mastery)
                log.info("  profile %s/%s (id=%s) mastery=%.2f", username, code, pid, mastery)

            log.info("=== model providers & models ===")
            providers = [
                ("OpenAI 兼容", "openai_compatible", "https://api.openai.com/v1",
                 "https://openai.com", "OpenAI 官方接口"),
                ("DeepSeek", "deepseek", "https://api.deepseek.com/v1",
                 "https://deepseek.com", "DeepSeek 大模型接口"),
                ("通义千问", "qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1",
                 "https://tongyi.aliyun.com", "阿里云通义千问"),
            ]
            provider_ids: Dict[str, int] = {}
            for name, code, base_url, website, desc in providers:
                provider_ids[code] = upsert_provider(cur, name, code, base_url, website, desc)

            models = [
                ("openai_compatible", "gpt-4o", "GPT-4o", 0.005, 0.015, "通用,代码,推理", 128000),
                ("openai_compatible", "gpt-4o-mini", "GPT-4o mini", 0.00015, 0.0006, "通用,代码", 128000),
                ("deepseek", "deepseek-chat", "DeepSeek Chat", 0.001, 0.002, "通用,推理,中文", 64000),
                ("deepseek", "deepseek-coder", "DeepSeek Coder", 0.001, 0.002, "代码,补全", 64000),
                ("qwen", "qwen-max", "通义千问 Max", 0.02, 0.06, "通用,长文本", 32000),
                ("qwen", "qwen-turbo", "通义千问 Turbo", 0.003, 0.006, "通用,快速", 32000),
                ("qwen", "qwen-long", "通义千问 Long", 0.0005, 0.002, "长文本,总结", 1000000),
                ("openai_compatible", "claude-3.5-sonnet", "Claude 3.5 Sonnet", 0.003, 0.015, "通用,推理", 200000),
            ]
            ai_model_ids: List[int] = []
            for pcode, mname, dname, ip, op, tags, ctx in models:
                mid = upsert_ai_model(cur, provider_ids[pcode], mname, dname, ip, op, tags, ctx)
                ai_model_ids.append(mid)
            log.info("  %d AI models seeded", len(ai_model_ids))

            log.info("=== task types ===")
            task_type_ids: Dict[str, int] = {}
            for code, name in TASK_TYPES:
                task_type_ids[code] = upsert_task_type(cur, code, name, f"{name}任务类型")

            log.info("=== projects + members + tasks + outputs ===")
            project_ids: Dict[str, int] = {}
            member_user_ids = {}
            for username, *_ in DEMO_USERS:
                member_user_ids[username] = get_user_id(cur, username)

            admin_id = member_user_ids["admin"]
            teacher_li_id = member_user_ids["teacher_li"]
            teacher_wang_id = member_user_ids["teacher_wang"]

            for proj_name, ptype, desc, owner_username, members in PROJECTS:
                owner_id = member_user_ids[owner_username]
                pid = upsert_project(cur, proj_name, ptype, desc, owner_id)
                project_ids[proj_name] = pid
                log.info("  project %s (id=%s)", proj_name, pid)

                # members
                upsert_project_member(cur, pid, owner_id, "teacher", 95.0)
                for m in members:
                    upsert_project_member(cur, pid, member_user_ids[m], "member",
                                           random.uniform(40, 90))

                # tasks per project
                if "数据库" in proj_name:
                    task_specs = [
                        ("lecture", "事务隔离级别图解讲义", "生成事务隔离级别的图解讲义", teacher_li_id,
                         member_user_ids["student_zhang"], "submitted", "high", 5),
                        ("quiz", "多表连接练习题集", "生成 20 道多表连接练习题", teacher_li_id,
                         member_user_ids["student_liu"], "approved", "normal", 7),
                        ("case", "银行转账并发案例", "生成一个银行转账并发的案例", teacher_li_id,
                         member_user_ids["student_zhang"], "running", "normal", 10),
                        ("review", "学生提交资源审核", "对上一批学生提交资源做审核", teacher_li_id,
                         None, "draft", "normal", 3),
                    ]
                elif "Python" in proj_name:
                    task_specs = [
                        ("lecture", "Flask 路由与蓝图", "Flask 路由与蓝图的入门讲义", teacher_wang_id,
                         member_user_ids["student_chen"], "approved", "normal", 4),
                        ("quiz", "Python 函数练习", "10 道函数相关练习题", teacher_wang_id,
                         member_user_ids["student_zhao"], "submitted", "normal", 6),
                        ("case", "数据看板实战案例", "完整的数据看板案例", teacher_wang_id,
                         member_user_ids["student_chen"], "running", "high", 8),
                    ]
                else:  # 软件工程
                    task_specs = [
                        ("summary", "Scrum 角色与流程总结", "Scrum 角色与流程的总结", teacher_wang_id,
                         member_user_ids["student_sun"], "approved", "normal", 2),
                        ("review", "团队迭代 1 评审", "对第一次迭代交付物进行评审", teacher_wang_id,
                         member_user_ids["student_zhou"], "submitted", "high", 5),
                    ]

                for ttype_code, title, tdesc, creator_id, assignee_id, status, prio, days in task_specs:
                    tid = upsert_project_task(
                        cur, pid, task_type_ids[ttype_code], title, tdesc,
                        creator_id, assignee_id, status, prio, days,
                    )
                    bid = upsert_branch(cur, pid, tid, f"主分支-{title[:8]}")
                    # invocation + output (only if task is past draft)
                    if status != "draft":
                        model_id = random.choice(ai_model_ids)
                        in_tok = random.randint(800, 4000)
                        out_tok = random.randint(400, 2500)
                        latency = random.randint(1200, 8500)
                        inv = upsert_invocation(
                            cur, pid, tid, bid, model_id, None,
                            f"请生成关于 {title} 的内容。\n\n要求：{tdesc}",
                            f"# {title}\n\n本文为多智能体协同生成的草稿。\n\n核心要点：\n1. 概念与原理\n2. 示例与代码\n3. 练习与思考\n\n（演示内容）",
                            in_tok, out_tok, latency,
                            round(in_tok * 0.001 / 1000 + out_tok * 0.002 / 1000, 4),
                            "success", creator_id,
                        )
                        upsert_cost_record(cur, inv, pid, tid, model_id, creator_id,
                                            in_tok, out_tok,
                                            in_tok * 0.001 / 1000, out_tok * 0.002 / 1000)
                        out_status = {
                            "submitted": "submitted",
                            "approved": "approved",
                            "rejected": "rejected",
                            "running": "generated",
                            "generated": "generated",
                        }.get(status, "draft")
                        out_id = upsert_output(
                            cur, tid, bid, inv, title,
                            f"# {title}\n\n（AI 生成内容）\n\n{tdesc}\n\n## 重点\n- 要点 1\n- 要点 2\n- 要点 3",
                            "ai_generated", out_status, creator_id,
                            is_final=(out_status == "approved"),
                        )
                        if status in ("submitted", "approved", "rejected"):
                            reviewer = teacher_li_id if creator_id == teacher_li_id else teacher_wang_id
                            req_id = upsert_review_request(
                                cur, out_id, tid, pid, creator_id, reviewer,
                                "approved" if status == "approved" else
                                "pending" if status == "submitted" else "rejected",
                                f"提交说明：{title}",
                            )
                            if status in ("approved", "rejected"):
                                upsert_review(
                                    cur=cur,
                                    request_id=req_id,
                                    output_id=out_id,
                                    reviewer_id=reviewer,
                                    accuracy=random.uniform(7.5, 9.5),
                                    completeness=random.uniform(7.0, 9.5),
                                    logic=random.uniform(7.0, 9.0),
                                    format_=random.uniform(7.0, 9.5),
                                    usability=random.uniform(7.0, 9.5),
                                    risk=random.uniform(0.5, 3.0),
                                    status="approved" if status == "approved" else "rejected",
                                    comment=("内容详实，逻辑清晰，可作为最终版本。" if status == "approved"
                                              else "需要补充错误案例和性能数据。"),
                                )
                        log_operation(cur, creator_id, pid, tid, "task_outputs", out_id,
                                       "submit" if status == "submitted" else "create",
                                       f"任务 {title} 进入 {status}")

            log.info("=== learning resources ===")
            for code in ("CS301", "CS201", "CS401"):
                cid = course_ids[code]
                kps = kp_ids_by_course[cid]
                for idx, (rtype, title, kps_subset) in enumerate([
                    ("lecture", f"{code} 课程概述讲义", kps[:3]),
                    ("quiz", f"{code} 阶段性测验题", kps[1:4]),
                    ("case", f"{code} 综合案例分析", kps[2:5]),
                ]):
                    kp_csv = ",".join(str(x) for x in kps_subset)
                    rid = upsert_learning_resource(
                        cur, cid, title, rtype, "intermediate",
                        f"# {title}\n\n本资源为多智能体协同生成的演示内容。",
                        kp_csv, "deepseek-chat", "approved", teacher_li_id if code == "CS301" else teacher_wang_id,
                    )

            log.info("=== learning feedbacks ===")
            for (uname, code), pid in profile_ids.items():
                student_id = member_user_ids[uname]
                # 2-3 feedback rows
                for i in range(2):
                    rid = fetchone(cur, "SELECT resource_id FROM learning_resources WHERE course_id=%s LIMIT 1",
                                    course_ids[code])
                    resource_id = rid["resource_id"] if rid else None
                    ftype = ["quiz_result", "self_report", "study_note"][i % 3]
                    score = round(random.uniform(0.55, 0.95), 3) if ftype == "quiz_result" else None
                    sm = round(random.uniform(0.5, 0.9), 3) if ftype in ("self_report", "study_note") else None
                    diff = random.choice(["appropriate", "too_hard", "appropriate"])
                    content = {
                        "quiz_result": f"第 {i+1} 次测验正确率 {int((score or 0)*100)}%",
                        "self_report": "我觉得这一节讲得清楚，例题有帮助。",
                        "study_note": "整理了关键概念的笔记。",
                    }[ftype]
                    upsert_feedback(cur, pid, course_ids[code], resource_id, ftype, content,
                                     score, sm, diff)

            log.info("=== operation logs ===")
            for uname, *_ in DEMO_USERS:
                uid = member_user_ids[uname]
                for action in ("login", "view", "create"):
                    log_operation(cur, uid, None, None, None, None, action,
                                   f"种子数据：{uname} 触发 {action}")

            log.info("=== login logs (success) ===")
            for uname, *_ in DEMO_USERS:
                uid = member_user_ids[uname]
                cur.execute(
                    """INSERT INTO login_logs (user_id, username, login_status, ip_address, user_agent)
                       VALUES (%s, %s, 'success', '127.0.0.1', 'seed-script/1.0')""",
                    (uid, uname),
                )

        conn.commit()
        log.info("=" * 60)
        log.info("Seed complete.")
        log.info("Demo login: any of %s", [u[0] for u in DEMO_USERS])
        log.info("Demo password: %s", DEMO_PASSWORD)
        log.info("=" * 60)
    except Exception:
        conn.rollback()
        log.exception("Seed failed, transaction rolled back.")
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
