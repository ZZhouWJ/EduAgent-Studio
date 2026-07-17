"""
Seed demo data for EduAgent Studio.

What it does
------------
- Inserts 1 admin, 1 teacher, 3 students with a configured bcrypt password.
- Ensures teacher / student roles are assigned.
- Ensures 3 courses exist and are owned by the demo teacher.
- Seeds knowledge points, student profiles, learning mastery, projects,
  project members, project tasks, task branches, task outputs,
  review requests, output reviews, learning resources, learning tasks,
  learning feedbacks, model providers, AI models, API configs,
  AI invocations, cost records, and a few operation/login logs.
- Idempotent: re-runnable. Stable dimensions are updated and the demo-owned
  activity graph is rebuilt in one transaction without duplicate accumulation.

How to run
----------
    cd /path/to/EduAgent-Studio
    read -s DEMO_PASSWORD && export DEMO_PASSWORD
    backend/.venv/bin/python database/seed_demo_data.py

Prereqs
-------
- .env configured (DB_HOST/DB_USER/DB_PASSWORD/DB_NAME point to MySQL).
- DEMO_PASSWORD is set to a unique value of at least 12 characters.
- MySQL is reachable and all production SQL migrations listed in
  ``database/README_A3.md`` have been applied.
- The bcrypt package is installed in the venv.
"""

from __future__ import annotations

import hashlib
import json
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
    env.update(
        {
            key: value
            for key, value in os.environ.items()
            if key.startswith("DB_") or key == "DEMO_PASSWORD"
        }
    )
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

DEMO_PASSWORD = ENV.get("DEMO_PASSWORD", "")
DEMO_PWHASH = ""

ROLE_METADATA = {
    "student_member": ("学生", "使用个性化辅导、学习路径、任务、资源与学习反馈", "active"),
    "teacher": ("教师", "管理本人课程、学生画像、学习任务、知识库与 AI 生成资源", "active"),
    "admin": ("系统管理员", "负责平台用户、课程、模型、智能体、审计、成本与内容安全治理", "active"),
    "project_leader": ("历史项目负责人", "旧协作模块兼容角色，当前教育平台不再分配", "disabled"),
}


# (username, real_name, email, student_no, phone, role_codes)
DEMO_USERS: List[Tuple[str, str, str, Optional[str], str, List[str]]] = [
    # admin
    ("admin", "系统管理员", "admin@eduagent.local", None, "13800000001", ["admin"]),
    # teacher
    ("teacher_li", "李建国", "li.jianguo@eduagent.local", None, "13800000010", ["teacher"]),
    # students
    ("student_zhang", "张小明", "zhang.xm@eduagent.local", "2024001001", "13800000201", ["student_member"]),
    ("student_liu", "刘洋", "liu.yang@eduagent.local", "2024001002", "13800000202", ["student_member"]),
    ("student_chen", "陈雨欣", "chen.yx@eduagent.local", "2024001003", "13800000203", ["student_member"]),
]

# Accounts introduced by old migrations, API smoke tests, and the previous
# nine-account demo. They are disabled by this seed so dashboards and account
# pickers show exactly the five supported contest identities.
RETIRED_SAMPLE_USERS: Tuple[str, ...] = (
    "teacher_wang",
    "student_zhao",
    "student_sun",
    "student_zhou",
    "student1",
    "teacher1",
    "apitest999",
    "newuser99",
    "testroleuser",
)


def upsert_user(cur, username: str, real_name: str, email: Optional[str],
                student_no: Optional[str], phone: str) -> int:
    row = fetchone(cur, "SELECT user_id FROM users WHERE username=%s", username)
    if row:
        uid = row["user_id"]
        cur.execute(
            """UPDATE users SET password_hash=%s, real_name=%s, email=%s, student_no=%s, phone=%s,
                                 status='active', is_deleted=0,
                                 deleted_at=NULL, deleted_by=NULL
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


def align_platform_roles(cur) -> None:
    """同步角色元数据，并停用不再分配的旧协作角色。"""
    for role_code, (role_name, description, status) in ROLE_METADATA.items():
        cur.execute(
            """UPDATE roles
               SET role_name=%s, description=%s, status=%s
               WHERE role_code=%s AND is_deleted=0""",
            (role_name, description, status, role_code),
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
     "teacher_li"),
    ("CS401", "软件工程实践",
     "软件工程方法论、需求分析、系统设计、项目管理、敏捷开发与持续集成",
     "teacher_li"),
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

MATERIAL_FILES = {
    "CS301": "database_system_principles.md",
    "CS201": "python_programming_guide.md",
    "CS401": "software_engineering_practice.md",
}

MATERIAL_GUIDANCE: Dict[str, str] = {
    "kp_db_intro": "数据库、数据库管理系统和应用共同构成数据管理环境。学习时需要区分模式、实例和视图，并说明 DBMS 对安全、并发和恢复的责任。",
    "kp_relational_model": "关系模型用关系、元组和属性表达数据，候选键确定唯一性，外键维护引用完整性。设计时应同时写清业务语义与约束。",
    "kp_sql_basic": "基础查询从输出列和数据来源开始，再依次处理筛选、分组、聚合和排序。WHERE 过滤行，HAVING 过滤分组后的结果。",
    "kp_sql_join": "连接查询必须先确认表间基数和连接条件。左连接用于保留左表未匹配记录，子查询与连接方案应结合空值和重复行验证。",
    "kp_index": "索引设计应由查询谓词、选择性、排序和执行计划共同驱动。复合索引字段顺序需要对应主要访问路径，并评估写入成本。",
    "kp_transaction": "事务通过原子性、一致性、隔离性和持久性保护业务不变量。边界应覆盖完整业务动作，失败时必须整体回滚。",
    "kp_concurrency": "并发控制需要识别脏读、不可重复读、幻读和丢失更新。隔离级别、锁顺序、超时重试必须结合具体数据库实现验证。",
    "kp_norm": "范式用于减少插入、更新和删除异常。反范式只能在明确性能证据下采用，并同步设计一致性维护和校验机制。",
    "kp_design": "数据库设计从需求和业务规则出发，经 E-R 模型转换为关系模式，再补充主外键、唯一约束、索引和审计字段。",
    "kp_py_syntax": "Python 基础包括对象引用、容器、分支和循环。实现前应先约定输入类型、空值和边界，再选择可读的数据结构。",
    "kp_py_func": "函数应有单一职责、清晰输入输出和稳定异常契约。模块用于组织相关能力，避免循环依赖和隐藏的全局状态。",
    "kp_py_oop": "类封装状态与行为，组合适合表达可替换协作关系。设计时应避免把数据访问、HTTP 处理和业务规则堆在同一对象中。",
    "kp_py_except": "异常处理只捕获可以处理的错误，并保留可诊断上下文。测试应覆盖成功、非法输入、资源不存在和依赖失败。",
    "kp_py_web": "Web 服务需明确路由、业务服务和数据访问边界，统一鉴权、错误响应与日志。接口契约应包含状态码和幂等要求。",
    "kp_se_process": "过程模型的选择取决于需求稳定性、风险和反馈周期。迭代开发需要目标、完成定义和可用增量，而不是无计划修改。",
    "kp_se_req": "可验收需求需明确参与者、触发条件、主流程、异常和量化标准。非功能需求必须转换为可测量指标。",
    "kp_se_design": "系统设计通过职责、接口、数据和部署视角降低耦合。关键决策要记录约束、替代方案、风险与演进方式。",
    "kp_se_agile": "Scrum 以产品目标、Sprint 目标和完成定义形成透明反馈。评审检查价值，回顾改进协作和工程实践。",
    "kp_se_test": "质量保障从需求阶段建立追溯关系，组合单元、接口和端到端测试。发布条件应包含自动化证据、监控和回滚方案。",
}

LEARNING_RESOURCE_CONTENTS: Dict[Tuple[str, str], str] = {
    ("CS301", "lecture"): """# 数据库系统原理学习导读

## 学习目标
- 说明数据库、数据库管理系统与应用系统之间的关系。
- 使用关系、元组、属性、主键和外键描述关系模型。
- 编写带筛选、排序与聚合的基础 SQL 查询。

## 知识主线
1. **数据管理**：数据库负责持久化数据，DBMS 负责定义、查询、约束、并发与恢复。
2. **关系模型**：表结构表达实体及联系，主键保证行唯一，外键维护表间引用完整性。
3. **查询过程**：先明确输出列与数据来源，再逐步添加筛选、分组、排序和结果数量限制。

## 示例任务
为选课系统设计 `student`、`course`、`enrollment` 三张表。列出每门课程的选课人数，并找出选课人数不少于 30 的课程。提交表结构、主外键说明和查询语句。

## 学习检查
- 能否区分模式、实例与视图？
- 能否解释实体完整性和参照完整性？
- 能否说明 `WHERE` 与 `HAVING` 的使用时机？""",
    ("CS301", "quiz"): """# 数据库系统原理阶段性测验

## 作答要求
本测验覆盖关系模型、基础 SQL、多表连接与子查询。先写结论，再说明依据；SQL 题需给出完整语句。

## 题目
1. 候选键、主键和外键分别解决什么问题？请用一个选课关系举例。（15 分）
2. 表 `score(student_id, course_id, grade)` 中，写出查询平均分高于 80 的课程及其平均分的 SQL。（20 分）
3. 说明内连接与左连接的结果差异，并给出应使用左连接的业务场景。（20 分）
4. 找出从未选修任何课程的学生，分别使用 `NOT EXISTS` 和左连接实现。（25 分）
5. 一条查询同时包含 `WHERE`、`GROUP BY`、`HAVING`、`ORDER BY`，写出它们的逻辑执行顺序。（20 分）

## 评分标准
- 结论与语法正确：60 分
- 能解释关系语义和空值影响：25 分
- 命名清晰、边界条件完整：15 分

完成后将错题对应到知识点，并记录错误原因，而不是只记录正确答案。""",
    ("CS301", "case"): """# 电商订单查询与索引优化案例

## 业务情境
订单系统包含用户、订单、订单明细和商品表。运营人员需要按时间、地区与商品类别统计销售额，当前月度报表耗时超过 12 秒。

## 任务
1. 设计四张表的主键、外键和关键约束。
2. 编写月度分区间销售额与订单量统计 SQL，正确处理取消订单。
3. 使用执行计划定位全表扫描、低选择性过滤或连接顺序问题。
4. 给出不超过 3 个索引方案，并说明字段顺序和适用查询。
5. 比较优化前后的执行计划、扫描行数和耗时。

## 约束
- 不允许以冗余索引替代分析。
- 金额统计必须说明精度与退款处理方式。
- 查询结果需覆盖无订单地区和空值场景。

## 验收标准
- SQL 结果与给定校验数据一致。
- 索引方案可由执行计划证据支撑。
- 报告包含风险、回滚方式和后续监控指标。""",
    ("CS201", "lecture"): """# Python 程序设计学习导读

## 学习目标
- 正确选择基础数据类型与控制结构。
- 使用函数、参数和模块拆分可复用逻辑。
- 通过类、对象与组合表达业务模型。

## 知识主线
1. **语法与数据**：变量引用对象，容器类型承担批量数据组织，不同类型具有不同的可变性。
2. **函数与模块**：函数应具有清晰输入输出；模块负责组织相关能力并控制依赖方向。
3. **面向对象**：类封装状态和行为，优先使用组合表达可替换协作关系。

## 示例任务
实现课程成绩统计模块：读取学生成绩，计算均值与等级分布，按课程输出报告。将读取、计算和展示拆成独立函数，并用 `CourseReport` 类封装一份报告。

## 学习检查
- 能否解释可变对象作为默认参数的风险？
- 能否区分位置参数、关键字参数与可变参数？
- 能否说明实例属性、类属性和方法的作用域？""",
    ("CS201", "quiz"): """# Python 程序设计阶段性测验

## 作答要求
本测验覆盖函数与模块、面向对象、异常处理与测试。代码题应包含异常分支和最小测试用例。

## 题目
1. 为什么不应把空列表直接作为函数默认参数？给出正确写法。（15 分）
2. 实现 `normalize_scores(scores)`：校验输入、过滤非法分数并返回 0 到 1 的归一化结果。（25 分）
3. 为课程、学生和选课记录建立类模型，说明你选择继承或组合的理由。（20 分）
4. 读取成绩文件时可能出现哪些异常？请设计异常处理边界，避免吞掉未知错误。（20 分）
5. 使用 `pytest` 风格写出正常、空输入和非法分数三个测试用例。（20 分）

## 评分标准
- 结果正确且边界明确：50 分
- 异常处理与类型契约合理：30 分
- 结构清晰、测试可重复：20 分""",
    ("CS201", "case"): """# 学习进度服务开发案例

## 业务情境
开发一个轻量学习进度服务，支持创建学习任务、更新完成度、查询逾期任务和返回课程汇总。服务需在输入错误和存储失败时返回可诊断结果。

## 任务
1. 使用类建模 `LearningTask` 与 `ProgressService`，明确状态转换规则。
2. 为创建、更新和查询操作设计函数接口与类型标注。
3. 使用 Flask 或 FastAPI 提供三个 HTTP 接口，并定义统一错误响应。
4. 为非法进度、重复任务和不存在任务编写异常与测试。
5. 将业务逻辑与 Web 路由分层，说明模块依赖关系。

## 验收标准
- 完成度只能在 0 到 100 之间且状态转换一致。
- 路由、业务逻辑和数据访问可独立测试。
- 至少覆盖成功、参数错误、资源不存在和内部异常四类测试。
- README 给出启动方式、接口示例和已知限制。""",
    ("CS401", "lecture"): """# 软件工程实践学习导读

## 学习目标
- 根据需求不确定性选择合适的软件过程。
- 将业务目标转化为可验证的功能与非功能需求。
- 从职责、接口、数据和部署视角形成系统设计。

## 知识主线
1. **过程模型**：瀑布、迭代、增量和敏捷适用于不同风险与反馈周期。
2. **需求工程**：需求需明确参与者、触发条件、主流程、异常和验收标准。
3. **系统设计**：模块边界应降低耦合，接口契约需覆盖数据、错误和版本演进。

## 示例任务
为校园预约系统完成一次从问题陈述到概要设计的推演：识别参与者和范围，编写核心用户故事及验收标准，绘制上下文关系并定义两个关键接口。

## 学习检查
- 能否说明迭代开发与无计划修改的区别？
- 能否把“系统要稳定”改写为可测量指标？
- 能否识别跨模块事务、权限和故障恢复风险？""",
    ("CS401", "quiz"): """# 软件工程实践阶段性测验

## 作答要求
本测验覆盖需求分析、系统设计、敏捷与 Scrum。答案必须结合场景和可验收证据。

## 题目
1. 将“平台操作简单”改写为两条可测量的非功能需求。（15 分）
2. 为“教师发布作业”编写用户故事、前置条件、主流程和两个异常流程。（25 分）
3. 某模块同时负责身份认证、报表和消息推送，指出设计问题并给出拆分依据。（20 分）
4. 说明 Product Backlog、Sprint Backlog 与 Increment 的关系。（20 分）
5. 需求在迭代中发生变化时，团队应如何评估影响并保持可追溯性？（20 分）

## 评分标准
- 需求可验证、场景完整：40 分
- 设计理由与权衡清楚：35 分
- 能体现追溯、风险和团队协作：25 分""",
    ("CS401", "case"): """# 校园预约平台迭代交付案例

## 业务情境
团队需要在两周内交付校园场地预约最小可用版本，支持资源查询、预约冲突检测、审批和取消。后续将接入消息通知与信用规则。

## 任务
1. 明确 MVP 范围、关键参与者和不在本迭代处理的事项。
2. 编写不少于 6 条用户故事，并为高优先级故事定义验收标准。
3. 设计模块边界、核心数据模型和预约冲突检测接口。
4. 建立 Sprint Backlog，估算工作量并说明依赖与风险。
5. 制定单元、接口和端到端测试策略，定义发布与回滚条件。

## 约束
- 审批和取消操作必须可审计。
- 同一场地同一时间段不得产生两个有效预约。
- 设计需预留通知能力，但本迭代不实现第三方短信。

## 验收标准
- 需求、设计、任务与测试之间可以双向追溯。
- 核心流程有自动化测试证据。
- 演示环境可重复部署，并提供已知风险与下一迭代计划。""",
}

PROJECT_OUTPUT_CONTENTS: Dict[str, str] = {
    "事务隔离级别图解讲义": """# 事务隔离级别图解讲义

## 学习目标
理解脏读、不可重复读和幻读的产生条件，并能根据一致性要求与并发代价选择隔离级别。

## 并发现象
| 现象 | 过程 | 风险 |
| --- | --- | --- |
| 脏读 | T1 修改后未提交，T2 已读到该值，随后 T1 回滚 | T2 基于不存在的数据继续计算 |
| 不可重复读 | T1 两次读取同一行，期间 T2 提交了更新 | 同一事务内行值不一致 |
| 幻读 | T1 两次执行同一范围查询，期间 T2 插入或删除匹配行 | 结果集行数发生变化 |

## 隔离级别
- **读未提交**：允许读取未提交数据，并发高但一致性风险最大。
- **读已提交**：每条语句读取已提交快照，可避免脏读。
- **可重复读**：事务内保持一致快照；具体幻读行为取决于数据库实现与锁策略。
- **串行化**：效果接近事务顺序执行，一致性最强，但等待与死锁概率上升。

## 判断方法
先标出每个事务的读写对象和提交点，再判断后一次读取是否必须看到前一次相同的版本。不要仅凭隔离级别名称推断，应结合数据库实现、查询范围和锁信息验证。

## 自检
库存扣减、余额查询和月度报表分别需要什么隔离保证？请说明允许出现的偏差、锁等待上限和失败重试策略。""",
    "多表连接练习题集": """# 多表连接练习题集

## 数据模型
使用学生 `student`、课程 `course`、教师 `teacher`、选课 `enrollment`、成绩 `score` 五张表。先画出主外键关系，再完成查询。

## 基础题（1-6）
1. 查询每名学生及其已选课程名称。
2. 查询每门课程及授课教师姓名。
3. 列出选修数据库课程的学生学号与姓名。
4. 查询每名学生的课程数，未选课学生也要显示为 0。
5. 查询没有任何学生选修的课程。
6. 查询同时选修数据库和 Python 的学生。

## 进阶题（7-14）
7. 统计每门课程的平均分、最高分与最低分。
8. 查询平均分高于全校平均分的学生。
9. 查询每门课程成绩排名前三的学生，正确处理并列。
10. 找出选课人数高于本院课程平均选课人数的课程。
11. 查询至少教授两门课程的教师及课程数。
12. 查询选修了某教师全部课程的学生。
13. 找出只选修一门课程且成绩及格的学生。
14. 查询每个院系平均分最高的课程。

## 综合题（15-20）
15. 生成学生成绩单，包含课程、学分、成绩和加权平均分。
16. 查询连续两个学期成绩提升的学生。
17. 识别同一时间段存在课程冲突的选课记录。
18. 查询先修课未通过却选修后续课程的学生。
19. 使用窗口函数统计课程成绩分位数，并解释与子查询方案的差异。
20. 为第 7、9、12 题分析执行计划并提出索引方案。

## 提交与评分
每题提交 SQL、结果行数和边界说明。正确性占 60%，空值与重复行处理占 20%，可读性占 10%，执行计划与索引依据占 10%。""",
    "银行转账并发案例": """# 银行转账并发案例

## 场景
账户 A 向账户 B 转账 500 元，同时账户 A 可能收到另一笔扣款。系统必须保证余额不为负、借贷两端金额守恒、重复请求不会重复入账。

## 初始数据
`account(id, balance, version)` 保存余额，`transfer(id, request_no, from_id, to_id, amount, status)` 保存转账流水，其中 `request_no` 唯一。

## 并发风险
1. 两个事务先后读取相同余额并分别扣减，造成丢失更新。
2. 借方已扣款但贷方写入失败，造成金额不守恒。
3. 客户端超时重试，造成同一请求重复转账。
4. 两笔反向转账以不同顺序锁定账户，造成死锁。

## 实现任务
- 在一个数据库事务内创建流水、锁定账户、校验余额、更新双方余额并提交。
- 始终按账户 ID 升序加锁，降低死锁概率。
- 以唯一请求号实现幂等；重复请求返回原流水结果。
- 对死锁与锁等待超时采用有上限的退避重试，并记录审计事件。

## 验证
并发执行 100 组转账，校验总余额不变、无负余额、请求号唯一、失败事务不产生单边记账。报告隔离级别、SQL、锁顺序、重试次数和最终校验结果。""",
    "Flask 路由与蓝图": """# Flask 路由与蓝图

## 学习目标
掌握 URL 规则、HTTP 方法、请求参数与响应状态码，并使用蓝图拆分可独立维护的业务模块。

## 路由契约
路由函数负责把 HTTP 请求转换为业务调用，再把结果转换为响应。参数校验失败返回 400，未认证返回 401，无权限返回 403，资源不存在返回 404；不要把所有异常都返回 200。

```python
students = Blueprint("students", __name__, url_prefix="/api/students")

@students.get("/<int:student_id>")
def get_student(student_id: int):
    student = student_service.get(student_id)
    if student is None:
        return {"message": "student not found"}, 404
    return student.to_dict(), 200
```

## 蓝图组织
- `routes.py`：声明路径、方法、输入与响应。
- `service.py`：实现业务规则，不依赖 Flask 全局请求对象。
- `repository.py`：封装持久化操作。
- `errors.py`：统一业务异常到 HTTP 响应的映射。

在应用工厂中注册蓝图，测试环境可注入独立配置与存储。跨域、鉴权、日志与追踪应通过扩展或中间件统一处理。

## 练习
实现学生列表和详情接口，支持分页与姓名筛选；分别测试成功、参数非法、资源不存在和仓储异常，确认状态码与错误结构一致。""",
    "Python 函数练习": """# Python 函数练习

## 要求
每题写出函数签名、类型标注、边界约定和至少两个测试用例。除题目明确允许外，不修改传入对象。

1. `clamp(value, lower, upper)`：将数值限制在闭区间内，并校验上下界。
2. `deduplicate(items)`：保持原顺序去重，支持不可哈希元素时给出明确策略。
3. `group_by(items, key)`：按回调结果分组，返回字典。
4. `moving_average(values, window)`：计算滑动平均，处理窗口大于序列长度的情况。
5. `retry(operation, attempts, retry_on)`：对指定异常执行有限重试。
6. `parse_score(text)`：解析成绩字符串，拒绝空值、非数字和区间外数值。
7. `compose(*functions)`：从右到左组合单参数函数。
8. `summarize(records, field)`：统计指定字段的数量、均值、最小值和最大值。
9. `memoize(function)`：实现保留函数元信息的简单缓存装饰器，并说明参数限制。
10. `batch(items, size)`：将可迭代对象按固定大小分批，最后一批允许不足。

## 评分标准
正确性 50%，边界与异常 20%，类型和可读性 15%，测试覆盖 15%。测试至少包含正常输入、空输入和一个非法输入。""",
    "数据看板实战案例": """# 数据看板实战案例

## 业务目标
为课程负责人构建学习数据看板，回答活跃学生数量、任务完成趋势、知识点薄弱分布和高风险学生变化四个问题。

## 数据与指标
- 学生活跃：按自然日去重的有效学习事件用户数。
- 任务完成率：截止时间内完成任务数除以到期任务数。
- 知识点掌握：最近有效测评按时间衰减后的加权结果。
- 风险学生：连续 7 天无学习、逾期任务不少于 2 个或掌握度显著下降。

## 实现任务
1. 使用 Flask 蓝图实现 `/api/dashboard/summary` 与 `/api/dashboard/trends`。
2. 在服务层定义统计口径、时间范围和权限范围，禁止学生读取全班数据。
3. 对高频聚合增加合适索引与短时缓存，并提供缓存失效策略。
4. 前端实现指标概览、趋势图、薄弱知识点排序和风险学生表格。
5. 为无数据、部分数据失败、超时和窄屏场景提供明确状态。

## 验收标准
接口口径可追溯，测试数据下计算结果准确；教师只能访问本人课程；图表有标题、单位和可读的键盘替代信息；首屏接口在目标数据量下 P95 小于 800ms。""",
    "Scrum 角色与流程总结": """# Scrum 角色与流程总结

## 三类责任
- **Product Owner**：最大化产品价值，管理并排序 Product Backlog，确保目标和条目清晰。
- **Scrum Master**：帮助团队理解并实践 Scrum，移除组织障碍，促进持续改进。
- **Developers**：共同制定 Sprint Backlog、保证交付质量，并对可用增量负责。

## 核心流程
1. Product Backlog 持续梳理，条目围绕产品目标排序。
2. Sprint Planning 明确 Sprint Goal，选择条目并制定实现计划。
3. Daily Scrum 检查实现 Sprint Goal 的进展并调整当天计划。
4. Sprint Review 与利益相关者检查增量并调整后续方向。
5. Sprint Retrospective 改进人员、协作、流程和工具。

## 三个工件及承诺
Product Backlog 对应 Product Goal，Sprint Backlog 对应 Sprint Goal，Increment 对应 Definition of Done。只有满足完成定义的工作才能计入增量。

## 常见误区
Daily Scrum 不是向管理者汇报；Scrum Master 不是任务分配者；Sprint Review 不是单纯演示会；未完成条目不能通过降低质量标准“转为完成”。团队应以透明、检查和适应形成可持续反馈闭环。""",
    "团队迭代 1 评审": """# 团队迭代 1 评审报告

## 评审范围
本次评审覆盖预约查询、预约创建、冲突检测与取消流程，以及对应需求、接口文档、自动化测试和部署说明。

## 结论
核心主流程可运行，但当前版本暂不满足发布条件。冲突检测在并发请求下缺少数据库唯一约束，取消操作未记录操作者与原因，接口错误结构也不一致。

## 发现
| 级别 | 问题 | 验收证据 |
| --- | --- | --- |
| 阻断 | 并发创建可能产生重叠预约 | 增加约束或事务锁，并通过并发测试 |
| 高 | 取消记录缺少审计字段 | 审计日志包含用户、时间、原因和原状态 |
| 中 | 400 与 404 响应结构不统一 | 契约测试覆盖全部公开接口 |
| 中 | 部署文档未说明回滚 | 提供版本回退和数据库兼容步骤 |

## 后续行动
负责人在下一次提交前修复阻断与高等级问题，补充并发、权限和回滚测试。修复后由评审人复核证据；中等级问题进入下一 Sprint，但必须明确负责人和截止时间。

## 通过条件
阻断和高等级问题归零，核心端到端测试通过，部署与回滚演练完成，遗留风险得到 Product Owner 明确认可。""",
}

LEGACY_KP_CODES = (
    "DB001", "DB002", "DB003", "DB005", "DB008", "DB012", "DB015", "DB020",
    "PY001", "PY002", "PY003", "PY004", "SE001", "SE002",
)


def upsert_kp(cur, course_id: int, code: str, name: str, difficulty: str, hours: float) -> int:
    row = fetchone(
        cur,
        "SELECT kp_id FROM knowledge_points WHERE course_id=%s AND kp_code=%s",
        course_id, code,
    )
    if row:
        cur.execute(
            """
            UPDATE knowledge_points
            SET kp_name=%s, difficulty_level=%s, estimated_hours=%s, is_deleted=0
            WHERE kp_id=%s
            """,
            (name, difficulty, hours, row["kp_id"]),
        )
        return row["kp_id"]
    cur.execute(
        """INSERT INTO knowledge_points
               (course_id, kp_name, kp_code, difficulty_level, estimated_hours, is_deleted)
           VALUES (%s, %s, %s, %s, %s, 0)""",
        (course_id, name, code, difficulty, hours),
    )
    return cur.lastrowid


def upsert_course_material(
    cur, course_id: int, course_code: str, created_by: int
) -> int:
    filename = MATERIAL_FILES[course_code]
    total_chars = sum(
        len(MATERIAL_GUIDANCE[kp_code])
        for kp_code, *_ in KNOWLEDGE_POINTS[course_code]
    )
    row = fetchone(
        cur,
        "SELECT material_id FROM course_materials WHERE course_id=%s AND filename=%s",
        course_id,
        filename,
    )
    if row:
        cur.execute(
            """UPDATE course_materials
               SET file_type='markdown', storage_path=%s, status='parsed',
                   error_message=NULL, total_chunks=%s, created_by=%s,
                   is_deleted=0, material_version=1, total_chars=%s,
                   last_reparse_at=NOW()
               WHERE material_id=%s""",
            (
                f"demo/course-materials/{filename}",
                len(KNOWLEDGE_POINTS[course_code]),
                created_by,
                total_chars,
                row["material_id"],
            ),
        )
        return row["material_id"]
    cur.execute(
        """INSERT INTO course_materials
               (course_id, filename, file_type, storage_path, status,
                total_chunks, created_by, is_deleted, material_version,
                total_chars, last_reparse_at)
           VALUES (%s, %s, 'markdown', %s, 'parsed', %s, %s, 0, 1, %s, NOW())""",
        (
            course_id,
            filename,
            f"demo/course-materials/{filename}",
            len(KNOWLEDGE_POINTS[course_code]),
            created_by,
            total_chars,
        ),
    )
    return cur.lastrowid


def upsert_material_chunk(
    cur,
    material_id: int,
    course_id: int,
    kp_id: int,
    kp_code: str,
    title: str,
    chunk_index: int,
) -> int:
    content = MATERIAL_GUIDANCE[kp_code]
    chunk_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    row = fetchone(
        cur,
        "SELECT chunk_id FROM course_material_chunks WHERE material_id=%s AND chunk_index=%s",
        material_id,
        chunk_index,
    )
    params = (
        course_id,
        kp_id,
        title,
        content,
        chunk_index + 1,
        chunk_index + 1,
        f"{title},{kp_code}",
        chunk_hash,
    )
    if row:
        cur.execute(
            """UPDATE course_material_chunks
               SET course_id=%s, kp_id=%s, title=%s, content=%s,
                   source_page=%s, source_paragraph=%s, bm25_terms=%s,
                   chunk_hash=%s, material_version=1, is_deleted=0
               WHERE chunk_id=%s""",
            (*params, row["chunk_id"]),
        )
        return row["chunk_id"]
    cur.execute(
        """INSERT INTO course_material_chunks
               (material_id, course_id, kp_id, title, content, source_page,
                source_paragraph, bm25_terms, chunk_index, chunk_hash,
                material_version, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 0)""",
        (
            material_id,
            course_id,
            kp_id,
            title,
            content,
            chunk_index + 1,
            chunk_index + 1,
            f"{title},{kp_code}",
            chunk_index,
            chunk_hash,
        ),
    )
    return cur.lastrowid


def prune_material_chunks(cur, material_id: int, expected_count: int) -> None:
    stale_rows = fetchall(
        cur,
        """SELECT chunk_id FROM course_material_chunks
           WHERE material_id=%s AND chunk_index >= %s""",
        material_id,
        expected_count,
    )
    stale_ids = [row["chunk_id"] for row in stale_rows]
    if not stale_ids:
        return
    placeholders = ",".join(["%s"] * len(stale_ids))
    cur.execute(
        f"DELETE FROM resource_evidence_links WHERE chunk_id IN ({placeholders})",
        stale_ids,
    )
    cur.execute(
        f"DELETE FROM kp_chunk_links WHERE chunk_id IN ({placeholders})",
        stale_ids,
    )
    cur.execute(
        f"DELETE FROM course_material_chunks WHERE chunk_id IN ({placeholders})",
        stale_ids,
    )
    log.info("  pruned %d stale chunks from material %s", len(stale_ids), material_id)


def upsert_kp_chunk_link(
    cur, chunk_id: int, kp_id: int, verified_by: int
) -> None:
    row = fetchone(
        cur,
        "SELECT link_id FROM kp_chunk_links WHERE chunk_id=%s AND kp_id=%s",
        chunk_id,
        kp_id,
    )
    if row:
        cur.execute(
            """UPDATE kp_chunk_links
               SET match_method='manual', relevance_score=0.9800,
                   status='confirmed', verified_by=%s, verified_at=NOW(),
                   match_version=1
               WHERE link_id=%s""",
            (verified_by, row["link_id"]),
        )
        return
    cur.execute(
        """INSERT INTO kp_chunk_links
               (chunk_id, kp_id, match_method, relevance_score, status,
                verified_by, verified_at, match_version)
           VALUES (%s, %s, 'manual', 0.9800, 'confirmed', %s, NOW(), 1)""",
        (chunk_id, kp_id, verified_by),
    )


# ---------------------------------------------------------------------------
# Student profiles & mastery
# ---------------------------------------------------------------------------

STUDENT_PROFILES: List[Tuple[str, str, str, str, str, int, float]] = [
    # (username, course_code, learning_goal, current_level, interests, weekly_hours, mastery_score)
    ("student_zhang", "CS301",
     "掌握数据库系统原理，独立完成数据库设计、复杂 SQL 与事务分析",
     "会写单表查询和 DDL，多表连接、事务隔离与索引设计薄弱",
     "数据库实践,Web开发,校园选课系统", 6, 0.38),
    ("student_liu", "CS201",
     "掌握 Python 工程化开发，能够独立实现带测试的 FastAPI 服务",
     "语法和函数基础扎实，异常边界、面向对象设计与自动化测试经验不足",
     "Python后端,数据分析,自动化测试", 8, 0.63),
    ("student_chen", "CS401",
     "能够组织一次完整敏捷迭代，完成需求、设计、测试和发布闭环",
     "有团队项目经验，擅长需求梳理，但系统设计与质量度量仍需加强",
     "产品设计,敏捷协作,质量保障", 10, 0.76),
]

PROFILE_TRAITS: Dict[str, Dict[str, str]] = {
    "student_zhang": {
        "knowledge_base": "完成数据库基础章节，能够使用 SELECT、WHERE、GROUP BY 与简单聚合。",
        "cognitive_style": "先看业务案例，再通过关系图和可执行 SQL 归纳概念。",
        "time_constraints": "工作日每天 45 分钟，周末可安排 2 小时集中练习。",
        "practice_level": "每周完成 2 组 SQL 练习，复杂查询需要分步提示。",
        "motivation": "希望在课程答辩中独立讲清选课系统的数据模型与事务设计。",
        "error_prone_points": "遗漏连接条件、混淆 WHERE 与 HAVING、无法判断并发现象。",
        "resource_preferences": "图解讲义,分步案例,即时测验",
    },
    "student_liu": {
        "knowledge_base": "熟悉 Python 容器、函数和模块，能完成小型脚本与基础接口。",
        "cognitive_style": "偏好先阅读接口契约，再通过代码重构和单元测试验证理解。",
        "time_constraints": "工作日晚间 1 小时，周六可进行 3 小时项目实践。",
        "practice_level": "能独立完成中等代码题，异常设计和测试覆盖需要反馈。",
        "motivation": "希望完成一个结构清晰、可测试、可部署的学习进度服务。",
        "error_prone_points": "可变默认参数、异常吞噬、业务逻辑与路由耦合。",
        "resource_preferences": "代码案例,错误分析,项目任务",
    },
    "student_chen": {
        "knowledge_base": "参与过两次课程团队项目，理解用户故事、迭代和基础测试流程。",
        "cognitive_style": "擅长从场景和角色出发，偏好模板、对比表与评审反馈。",
        "time_constraints": "每周可投入 10 小时，周三与周日适合团队协作。",
        "practice_level": "能主持需求评审，正在提升架构权衡和质量指标设计能力。",
        "motivation": "希望担任迭代负责人，形成可追溯、可验收的交付方案。",
        "error_prone_points": "非功能需求不可测、模块职责过宽、风险缺少责任人。",
        "resource_preferences": "项目案例,评审清单,可视化看板",
    },
}


def upsert_student_profile(cur, student_id: int, course_id: int, goal: str, level: str,
                            interests: str, weekly_hours: int, mastery: float,
                            traits: Dict[str, str]) -> int:
    row = fetchone(
        cur,
        "SELECT profile_id FROM student_profiles WHERE student_id=%s AND course_id=%s",
        student_id, course_id,
    )
    if row:
        pid = row["profile_id"]
        cur.execute(
            """UPDATE student_profiles
               SET learning_goal=%s, knowledge_base=%s, current_level=%s,
                   cognitive_style=%s, time_constraints=%s, practice_level=%s,
                   motivation=%s, error_prone_points=%s, interests=%s,
                   resource_preferences=%s, weekly_hours=%s,
                   mastery_score=%s, is_deleted=0, deleted_at=NULL
               WHERE profile_id=%s""",
            (
                goal,
                traits["knowledge_base"],
                level,
                traits["cognitive_style"],
                traits["time_constraints"],
                traits["practice_level"],
                traits["motivation"],
                json.dumps(
                    traits["error_prone_points"].split("、"), ensure_ascii=False
                ),
                interests,
                traits["resource_preferences"],
                weekly_hours,
                mastery,
                pid,
            ),
        )
        return pid
    cur.execute(
        """INSERT INTO student_profiles
               (student_id, course_id, learning_goal, knowledge_base,
                current_level, cognitive_style, time_constraints,
                practice_level, motivation, error_prone_points, interests,
                resource_preferences, weekly_hours, mastery_score, is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)""",
        (
            student_id,
            course_id,
            goal,
            traits["knowledge_base"],
            level,
            traits["cognitive_style"],
            traits["time_constraints"],
            traits["practice_level"],
            traits["motivation"],
            json.dumps(
                traits["error_prone_points"].split("、"), ensure_ascii=False
            ),
            interests,
            traits["resource_preferences"],
            weekly_hours,
            mastery,
        ),
    )
    return cur.lastrowid


def seed_mastery(
    cur, profile_id: int, kp_ids: List[int], base: float, seed_key: str
) -> None:
    """Fill per-KP mastery around `base` with noise; skips if row exists."""
    rng = random.Random(seed_key)
    for kp_id in kp_ids:
        score = max(0.05, min(0.95, base + rng.uniform(-0.20, 0.25)))
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
                (round(score, 3), round(score + rng.uniform(-0.05, 0.1), 3),
                 date.today() - timedelta(days=rng.randint(1, 14)),
                 "系统根据近期测验自动更新", row["mastery_id"]),
            )
        else:
            cur.execute(
                """INSERT INTO student_knowledge_mastery
                       (profile_id, kp_id, mastery_level, last_test_score,
                        last_test_date, update_reason, is_deleted)
                   VALUES (%s, %s, %s, %s, %s, '系统根据近期测验自动更新', 0)""",
                (profile_id, kp_id, round(score, 3),
                 round(score + rng.uniform(-0.05, 0.1), 3),
                 date.today() - timedelta(days=rng.randint(1, 14))),
            )


def seed_profile_activity(
    cur, profile_id: int, course_id: int, username: str, learning_goal: str
) -> None:
    traits = PROFILE_TRAITS[username]
    dialog_rows = (
        (
            "student",
            f"我的目标是{learning_goal}。每周学习安排是：{traits['time_constraints']}",
            {"learning_goal": learning_goal, "time_constraints": traits["time_constraints"]},
        ),
        (
            "assistant",
            f"已记录目标。后续资源将优先采用{traits['resource_preferences']}，并重点关注{traits['error_prone_points']}。",
            {
                "resource_preferences": traits["resource_preferences"],
                "error_prone_points": traits["error_prone_points"],
            },
        ),
    )
    for role, content, extracted in dialog_rows:
        row = fetchone(
            cur,
            """SELECT message_id FROM profile_dialog_messages
               WHERE profile_id=%s AND role=%s AND content=%s LIMIT 1""",
            profile_id,
            role,
            content,
        )
        if row:
            cur.execute(
                """UPDATE profile_dialog_messages
                   SET extracted_json=%s, is_applied=1, is_deleted=0
                   WHERE message_id=%s""",
                (json.dumps(extracted, ensure_ascii=False), row["message_id"]),
            )
        else:
            cur.execute(
                """INSERT INTO profile_dialog_messages
                       (profile_id, role, content, extracted_json, is_applied, is_deleted)
                   VALUES (%s, %s, %s, %s, 1, 0)""",
                (
                    profile_id,
                    role,
                    content,
                    json.dumps(extracted, ensure_ascii=False),
                ),
            )

    summary = "演示初始化：根据诊断对话补充目标、时间约束、偏好和易错点"
    row = fetchone(
        cur,
        """SELECT history_id FROM profile_update_history
           WHERE profile_id=%s AND change_summary=%s LIMIT 1""",
        profile_id,
        summary,
    )
    if not row:
        cur.execute(
            """INSERT INTO profile_update_history
                   (profile_id, update_type, before_json, after_json, change_summary)
               VALUES (%s, 'dialog', %s, %s, %s)""",
            (
                profile_id,
                json.dumps({}, ensure_ascii=False),
                json.dumps(
                    {
                        "course_id": course_id,
                        "learning_goal": learning_goal,
                        **traits,
                    },
                    ensure_ascii=False,
                ),
                summary,
            ),
        )

    tutor_rows = (
        (
            f"我在本课程最容易出错的地方是什么？",
            f"当前画像显示需要优先关注：{traits['error_prone_points']}。建议先完成一个诊断题，再按错误类型选择讲义和练习。",
            "basic",
            1,
            "请给我一份 30 分钟的练习安排。",
        ),
        (
            "如何判断我是否真正掌握了本周知识点？",
            "同时检查三类证据：能否解释概念、能否独立完成新题、能否说明错误原因。系统会结合测验、任务进度和自评更新掌握度。",
            "intermediate",
            None,
            None,
        ),
    )
    for question, answer, level, helpful, follow_up in tutor_rows:
        row = fetchone(
            cur,
            "SELECT session_id FROM tutor_sessions WHERE profile_id=%s AND question=%s LIMIT 1",
            profile_id,
            question,
        )
        if row:
            cur.execute(
                """UPDATE tutor_sessions
                   SET course_id=%s, answer=%s, explanation_level=%s,
                       helpful=%s, follow_up=%s, is_deleted=0
                   WHERE session_id=%s""",
                (course_id, answer, level, helpful, follow_up, row["session_id"]),
            )
        else:
            cur.execute(
                """INSERT INTO tutor_sessions
                       (profile_id, course_id, question, answer, explanation_level,
                        helpful, follow_up, is_deleted)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 0)""",
                (profile_id, course_id, question, answer, level, helpful, follow_up),
            )


def refresh_profile_mastery_score(cur, profile_id: int) -> float:
    """Derive the profile summary from its persisted knowledge-point evidence."""
    cur.execute(
        """UPDATE student_profiles sp
           SET sp.mastery_score = COALESCE(
               (SELECT AVG(skm.mastery_level)
                FROM student_knowledge_mastery skm
                WHERE skm.profile_id = sp.profile_id AND skm.is_deleted = 0),
               sp.mastery_score
           )
           WHERE sp.profile_id = %s AND sp.is_deleted = 0""",
        (profile_id,),
    )
    row = fetchone(
        cur,
        "SELECT mastery_score FROM student_profiles WHERE profile_id=%s",
        profile_id,
    )
    return float(row["mastery_score"]) if row else 0.0


def upsert_learning_task(
    cur,
    course_id: int,
    title: str,
    description: str,
    target_kp_ids: List[int],
    assignee_id: Optional[int],
    creator_id: int,
    status: str,
    due_days: Optional[int],
) -> int:
    row = fetchone(
        cur,
        "SELECT task_id FROM learning_tasks WHERE course_id=%s AND title=%s",
        course_id,
        title,
    )
    kp_value = ",".join(str(kp_id) for kp_id in target_kp_ids)
    due_date = datetime.now() + timedelta(days=due_days) if due_days else None
    if row:
        cur.execute(
            """
            UPDATE learning_tasks
            SET description=%s,
                target_kp_ids=%s,
                assignee_id=%s,
                creator_id=%s,
                status=%s,
                due_date=%s,
                is_deleted=0,
                updated_at=NOW()
            WHERE task_id=%s
            """,
            (
                description,
                kp_value,
                assignee_id,
                creator_id,
                status,
                due_date,
                row["task_id"],
            ),
        )
        return row["task_id"]
    cur.execute(
        """
        INSERT INTO learning_tasks
            (course_id, title, description, target_kp_ids, assignee_id,
             due_date, creator_id, status, is_deleted, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, NOW(), NOW())
        """,
        (
            course_id,
            title,
            description,
            kp_value,
            assignee_id,
            due_date,
            creator_id,
            status,
        ),
    )
    return cur.lastrowid


def upsert_learning_task_progress(
    cur, task_id: int, student_id: int, status: str
) -> None:
    started_at = datetime.now() - timedelta(days=2) if status != "assigned" else None
    completed_at = datetime.now() - timedelta(hours=8) if status == "completed" else None
    row = fetchone(
        cur,
        """SELECT progress_id FROM learning_task_progress
           WHERE task_id=%s AND student_id=%s""",
        task_id,
        student_id,
    )
    if row:
        cur.execute(
            """UPDATE learning_task_progress
               SET status=%s, started_at=%s, completed_at=%s,
                   is_deleted=0, updated_at=NOW()
               WHERE progress_id=%s""",
            (status, started_at, completed_at, row["progress_id"]),
        )
        return
    cur.execute(
        """INSERT INTO learning_task_progress
               (task_id, student_id, status, started_at, completed_at,
                is_deleted, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, 0, NOW(), NOW())""",
        (task_id, student_id, status, started_at, completed_at),
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
     "teacher_li",
     ["student_liu", "student_chen"]),
    ("软件工程 - 团队协作流程演练",
     "教学项目",
     "按 Scrum 流程完成一个小型 Web 应用的迭代开发",
     "teacher_li",
     ["student_zhang", "student_liu", "student_chen"]),
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
                                            generation_agent='multi_agent_workflow',
                                            status=%s, created_by=%s, is_deleted=0,
                                            deleted_at=NULL, updated_at=NOW()
               WHERE resource_id=%s""",
            (rtype, difficulty, content, kp_ids_csv, model, status, created_by, rid),
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


def upsert_resource_review(
    cur,
    resource_id: int,
    submitter_id: int,
    reviewer_id: int,
    status: str,
) -> None:
    row = fetchone(
        cur,
        """SELECT review_id FROM learning_resource_reviews
           WHERE resource_id=%s AND submitter_id=%s ORDER BY review_id DESC LIMIT 1""",
        resource_id,
        submitter_id,
    )
    reviewed = status != "pending"
    scores = {
        "approved": (9.2, 8.8, 9.0, 8.7, 9.1),
        "rejected": (6.2, 5.8, 6.5, 7.0, 5.9),
        "pending": (None, None, None, None, None),
    }[status]
    comment = {
        "approved": "事实准确，知识点覆盖完整，案例和练习可直接用于教学。",
        "rejected": "需要补充来源证据、边界条件与可验证的答案解析后重新送审。",
        "pending": "等待教师完成内容准确性、证据充分性和教学可用性审核。",
    }[status]
    params = (
        reviewer_id,
        status,
        "多智能体生成完成，提交课程内容审核。",
        *scores,
        comment,
        datetime.now() if reviewed else None,
    )
    if row:
        cur.execute(
            """UPDATE learning_resource_reviews
               SET reviewer_id=%s, review_status=%s, submit_note=%s,
                   accuracy_score=%s, completeness_score=%s, logic_score=%s,
                   format_score=%s, usability_score=%s, review_comment=%s,
                   reviewed_at=%s, is_deleted=0, updated_at=NOW()
               WHERE review_id=%s""",
            (*params, row["review_id"]),
        )
        return
    cur.execute(
        """INSERT INTO learning_resource_reviews
               (resource_id, submitter_id, reviewer_id, review_status,
                submit_note, accuracy_score, completeness_score, logic_score,
                format_score, usability_score, review_comment, reviewed_at,
                is_deleted)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)""",
        (resource_id, submitter_id, *params),
    )


def upsert_resource_evidence(
    cur,
    resource_id: int,
    chunk_id: int,
    kp_id: int,
    quote_text: str,
    resource_status: str,
    verified_by: int,
    source_page: int,
) -> None:
    verified_status = {
        "approved": "verified",
        "rejected": "rejected",
    }.get(resource_status, "pending")
    usage_type = "conceptual" if resource_status == "draft" else "paraphrase"
    row = fetchone(
        cur,
        """SELECT link_id FROM resource_evidence_links
           WHERE resource_id=%s AND chunk_id=%s AND kp_id=%s LIMIT 1""",
        resource_id,
        chunk_id,
        kp_id,
    )
    params = (
        quote_text,
        0.9400,
        usage_type,
        verified_status,
        verified_by if verified_status != "pending" else None,
        datetime.now() if verified_status != "pending" else None,
        source_page,
        1,
    )
    if row:
        cur.execute(
            """UPDATE resource_evidence_links
               SET quote_text=%s, relevance_score=%s, usage_type=%s,
                   verified_status=%s, verified_by=%s, verified_at=%s,
                   source_page=%s, source_paragraph=%s
               WHERE link_id=%s""",
            (*params, row["link_id"]),
        )
        return
    cur.execute(
        """INSERT INTO resource_evidence_links
               (resource_id, chunk_id, kp_id, quote_text, relevance_score,
                usage_type, verified_status, verified_by, verified_at,
                source_page, source_paragraph)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (resource_id, chunk_id, kp_id, *params),
    )


def upsert_feedback(cur, profile_id: int, course_id: int, resource_id: Optional[int],
                     ftype: str, content: str, score: Optional[float],
                     self_mastery: Optional[float], difficulty: str) -> int:
    row = fetchone(
        cur,
        """
        SELECT feedback_id
        FROM learning_feedbacks
        WHERE profile_id=%s
          AND course_id=%s
          AND resource_id <=> %s
          AND feedback_type=%s
          AND content=%s
        LIMIT 1
        """,
        profile_id,
        course_id,
        resource_id,
        ftype,
        content,
    )
    if row:
        cur.execute(
            """
            UPDATE learning_feedbacks
            SET quiz_score=%s,
                self_mastery=%s,
                difficulty_rating=%s,
                is_deleted=0,
                updated_at=NOW()
            WHERE feedback_id=%s
            """,
            (score, self_mastery, difficulty, row["feedback_id"]),
        )
        return row["feedback_id"]
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
    global DEMO_PWHASH
    if len(DEMO_PASSWORD) < 12 or DEMO_PASSWORD.lower().startswith(
        ("change_me", "replace_")
    ):
        log.error("Set DEMO_PASSWORD to a unique value of at least 12 characters.")
        return 2
    DEMO_PWHASH = hash_password(DEMO_PASSWORD)
    random.seed(20260717)

    conn = connect()
    try:
        with conn.cursor() as cur:
            # 0) Rebuild project-workflow fixtures while preserving stable
            #    users, profiles, course resources, feedbacks, and learning tasks.
            active_demo_usernames = [u[0] for u in DEMO_USERS]
            demo_usernames = active_demo_usernames + list(RETIRED_SAMPLE_USERS)
            log.info("=== cleanup previous demo rows (idempotent) ===")
            placeholders = ",".join(["%s"] * len(demo_usernames))

            # We only ever delete data we previously inserted, and our cleanup
            # is bounded by the demo usernames / owner_id list, so disabling FK
            # checks is safe and avoids the chore of manually ordering
            # parent/child deletions across 30+ tables.
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")

            legacy_placeholders = ",".join(["%s"] * len(LEGACY_KP_CODES))
            cur.execute(
                f"UPDATE knowledge_points SET is_deleted=1 "
                f"WHERE kp_code IN ({legacy_placeholders})",
                LEGACY_KP_CODES,
            )

            # Remove the complete education-side graph belonging to known
            # samples. Stable courses and materials are kept and updated below.
            profile_children = (
                "student_knowledge_mastery",
                "learning_feedbacks",
                "profile_dialog_messages",
                "profile_update_history",
                "tutor_sessions",
            )
            for table in profile_children:
                cur.execute(
                    f"DELETE {table} FROM {table} "
                    f"INNER JOIN student_profiles sp ON {table}.profile_id=sp.profile_id "
                    f"INNER JOIN users u ON sp.student_id=u.user_id "
                    f"WHERE u.username IN ({placeholders})",
                    demo_usernames,
                )

            # Old migrations left child rows attached to missing or soft-deleted
            # profiles. They have no observable owner and distort analytics.
            for table in profile_children:
                cur.execute(
                    f"DELETE {table} FROM {table} "
                    f"LEFT JOIN student_profiles sp ON {table}.profile_id=sp.profile_id "
                    f"WHERE sp.profile_id IS NULL OR sp.is_deleted=1"
                )
            cur.execute(
                """DELETE sp FROM student_profiles sp
                   LEFT JOIN users u ON sp.student_id=u.user_id
                   WHERE sp.is_deleted=1 OR u.user_id IS NULL OR u.is_deleted=1"""
            )

            # Preserve historical system invocations while removing broken user
            # references left by old hard-deleted sample accounts.
            cur.execute(
                """UPDATE ai_invocations ai
                   LEFT JOIN users u ON ai.created_by=u.user_id
                   SET ai.created_by=NULL
                   WHERE ai.created_by IS NOT NULL AND u.user_id IS NULL"""
            )

            cur.execute(
                f"DELETE ltp FROM learning_task_progress ltp "
                f"INNER JOIN users u ON ltp.student_id=u.user_id "
                f"WHERE u.username IN ({placeholders})",
                demo_usernames,
            )
            cur.execute(
                f"DELETE ltp FROM learning_task_progress ltp "
                f"INNER JOIN learning_tasks lt ON ltp.task_id=lt.task_id "
                f"INNER JOIN users u ON lt.creator_id=u.user_id "
                f"WHERE u.username IN ({placeholders})",
                demo_usernames,
            )
            cur.execute(
                f"DELETE FROM learning_tasks WHERE creator_id IN "
                f"(SELECT user_id FROM users WHERE username IN ({placeholders})) "
                f"OR assignee_id IN "
                f"(SELECT user_id FROM users WHERE username IN ({placeholders}))",
                (*demo_usernames, *demo_usernames),
            )

            cur.execute(
                f"DELETE rel FROM resource_evidence_links rel "
                f"INNER JOIN learning_resources lr ON rel.resource_id=lr.resource_id "
                f"INNER JOIN users u ON lr.created_by=u.user_id "
                f"WHERE u.username IN ({placeholders})",
                demo_usernames,
            )
            cur.execute(
                f"DELETE lrr FROM learning_resource_reviews lrr "
                f"INNER JOIN learning_resources lr ON lrr.resource_id=lr.resource_id "
                f"INNER JOIN users u ON lr.created_by=u.user_id "
                f"WHERE u.username IN ({placeholders})",
                demo_usernames,
            )
            cur.execute(
                f"DELETE lr FROM learning_resources lr "
                f"INNER JOIN users u ON lr.created_by=u.user_id "
                f"WHERE u.username IN ({placeholders})",
                demo_usernames,
            )
            cur.execute(
                f"DELETE sp FROM student_profiles sp "
                f"INNER JOIN users u ON sp.student_id=u.user_id "
                f"WHERE u.username IN ({placeholders})",
                demo_usernames,
            )

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
                ("project_tasks", "creator_id"),
                ("project_members", "user_id"),
                ("operation_logs", "user_id"),
                ("auth_sessions", "user_id"),
                ("user_roles", "user_id"),
            ]
            for tbl, col in USER_COL:
                cur.execute(
                    f"DELETE {tbl} FROM {tbl} "
                    f"INNER JOIN users u ON {tbl}.{col} = u.user_id "
                    f"WHERE u.username IN ({placeholders})",
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
            cur.execute(
                """
                DELETE ts
                FROM tutor_sessions ts
                LEFT JOIN student_profiles sp
                  ON ts.profile_id = sp.profile_id AND sp.is_deleted = 0
                WHERE sp.profile_id IS NULL
                """
            )
            # Re-enable FK checks now that demo rows are gone.
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            log.info("  cleanup done")

            log.info("=== users & roles ===")
            align_platform_roles(cur)
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

            admin_id = get_user_id(cur, "admin")
            retired_placeholders = ",".join(["%s"] * len(RETIRED_SAMPLE_USERS))
            cur.execute(
                f"""UPDATE users
                    SET status='disabled', is_deleted=1, deleted_at=NOW(),
                        deleted_by=%s, updated_at=NOW()
                    WHERE username IN ({retired_placeholders})""",
                (admin_id, *RETIRED_SAMPLE_USERS),
            )

            log.info("=== courses ===")
            course_ids: Dict[str, int] = {}
            for code, name, desc, owner_username in COURSES:
                owner_id = get_user_id(cur, owner_username)
                cid = upsert_course(cur, code, name, desc, owner_id)
                course_ids[code] = cid
                log.info("  course %s (id=%s) owner=%s", code, cid, owner_username)

            log.info("=== knowledge points ===")
            kp_ids_by_course: Dict[int, List[int]] = {}
            kp_id_by_code: Dict[str, int] = {}
            for code, kps in KNOWLEDGE_POINTS.items():
                cid = course_ids[code]
                ids = []
                for kcode, kname, diff, hours in kps:
                    kid = upsert_kp(cur, cid, kcode, kname, diff, hours)
                    ids.append(kid)
                    kp_id_by_code[kcode] = kid
                kp_ids_by_course[cid] = ids
                log.info("  %s: %d knowledge points", code, len(ids))

            log.info("=== course materials + chunks + knowledge links ===")
            teacher_li_id = get_user_id(cur, "teacher_li")
            chunk_by_kp: Dict[int, Dict[str, Any]] = {}
            for code, kps in KNOWLEDGE_POINTS.items():
                cid = course_ids[code]
                material_id = upsert_course_material(
                    cur, cid, code, teacher_li_id
                )
                prune_material_chunks(cur, material_id, len(kps))
                for index, (kp_code, kp_name, _difficulty, _hours) in enumerate(kps):
                    kp_id = kp_id_by_code[kp_code]
                    chunk_id = upsert_material_chunk(
                        cur,
                        material_id,
                        cid,
                        kp_id,
                        kp_code,
                        kp_name,
                        index,
                    )
                    upsert_kp_chunk_link(cur, chunk_id, kp_id, teacher_li_id)
                    chunk_by_kp[kp_id] = {
                        "chunk_id": chunk_id,
                        "content": MATERIAL_GUIDANCE[kp_code],
                        "source_page": index + 1,
                    }
                log.info("  %s: material=%s, chunks=%d", code, material_id, len(kps))

            log.info("=== student profiles + mastery ===")
            profile_ids: Dict[Tuple[str, str], int] = {}
            for username, code, goal, level, interests, weekly, mastery in STUDENT_PROFILES:
                student_id = get_user_id(cur, username)
                cid = course_ids[code]
                pid = upsert_student_profile(cur, student_id, cid, goal, level,
                                              interests, weekly, mastery,
                                              PROFILE_TRAITS[username])
                profile_ids[(username, code)] = pid
                seed_mastery(
                    cur,
                    pid,
                    kp_ids_by_course[cid],
                    mastery,
                    f"{username}:{code}",
                )
                actual_mastery = refresh_profile_mastery_score(cur, pid)
                seed_profile_activity(cur, pid, cid, username, goal)
                log.info(
                    "  profile %s/%s (id=%s) mastery=%.3f",
                    username,
                    code,
                    pid,
                    actual_mastery,
                )

            log.info("=== learning tasks ===")
            learning_task_specs = [
                (
                    "CS301",
                    "数据库事务与并发控制",
                    "学习事务的 ACID 特性，掌握隔离级别及并发控制方法",
                    [5, 6],
                    "student_zhang",
                    "in_progress",
                    4,
                ),
                (
                    "CS301",
                    "SQL多表连接练习",
                    "完成教务系统多表查询练习，包括 INNER JOIN 和 LEFT JOIN",
                    [3],
                    "student_zhang",
                    "assigned",
                    -2,
                ),
                (
                    "CS201",
                    "Python函数与模块练习",
                    "编写包含类型标注和单元测试的 Python 模块，实现学习记录统计",
                    [1],
                    "student_liu",
                    "completed",
                    -3,
                ),
                (
                    "CS201",
                    "FastAPI异常处理与接口测试",
                    "实现统一错误响应，并覆盖参数错误、资源不存在和依赖失败场景",
                    [3, 4],
                    "student_liu",
                    "assigned",
                    7,
                ),
                (
                    "CS401",
                    "UML建模实践",
                    "为校园预约平台绘制用例图、领域模型和模块依赖图",
                    [1, 2],
                    "student_chen",
                    "in_progress",
                    5,
                ),
                (
                    "CS401",
                    "Sprint评审与质量复盘",
                    "依据完成定义检查需求、测试、发布与回滚证据并形成复盘记录",
                    [3, 4],
                    "student_chen",
                    "completed",
                    -1,
                ),
            ]
            for code, title, desc, kp_indexes, assignee_name, status, due_days in learning_task_specs:
                cid = course_ids[code]
                task_id = upsert_learning_task(
                    cur,
                    cid,
                    title,
                    desc,
                    [kp_ids_by_course[cid][index] for index in kp_indexes],
                    get_user_id(cur, assignee_name),
                    get_user_id(cur, COURSES[[item[0] for item in COURSES].index(code)][3]),
                    status,
                    due_days,
                )
                assignee_id = get_user_id(cur, assignee_name)
                upsert_learning_task_progress(
                    cur, task_id, assignee_id, status
                )
                log.info("  task %s (id=%s)", title, task_id)

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
                        ("lecture", "Flask 路由与蓝图", "Flask 路由与蓝图的入门讲义", teacher_li_id,
                         member_user_ids["student_liu"], "approved", "normal", 4),
                        ("quiz", "Python 函数练习", "10 道函数相关练习题", teacher_li_id,
                         member_user_ids["student_liu"], "submitted", "normal", 6),
                        ("case", "数据看板实战案例", "完整的数据看板案例", teacher_li_id,
                         member_user_ids["student_chen"], "running", "high", 8),
                    ]
                else:  # 软件工程
                    task_specs = [
                        ("summary", "Scrum 角色与流程总结", "Scrum 角色与流程的总结", teacher_li_id,
                         member_user_ids["student_chen"], "approved", "normal", 2),
                        ("review", "团队迭代 1 评审", "对第一次迭代交付物进行评审", teacher_li_id,
                         member_user_ids["student_zhang"], "submitted", "high", 5),
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
                            PROJECT_OUTPUT_CONTENTS[title],
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
                            PROJECT_OUTPUT_CONTENTS[title],
                            "ai_generated", out_status, creator_id,
                            is_final=(out_status == "approved"),
                        )
                        if status in ("submitted", "approved", "rejected"):
                            reviewer = teacher_li_id
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
            resource_statuses = {
                "CS301": ("approved", "pending_review", "rejected"),
                "CS201": ("approved", "approved", "pending_review"),
                "CS401": ("approved", "draft", "approved"),
            }
            for code in ("CS301", "CS201", "CS401"):
                cid = course_ids[code]
                kps = kp_ids_by_course[cid]
                for idx, (rtype, title, kps_subset) in enumerate([
                    ("lecture", f"{code} 课程概述讲义", kps[:3]),
                    ("quiz", f"{code} 阶段性测验题", kps[1:4]),
                    ("case", f"{code} 综合案例分析", kps[2:5]),
                ]):
                    kp_csv = ",".join(str(x) for x in kps_subset)
                    resource_status = resource_statuses[code][idx]
                    rid = upsert_learning_resource(
                        cur, cid, title, rtype, "intermediate",
                        LEARNING_RESOURCE_CONTENTS[(code, rtype)],
                        kp_csv, "deepseek-chat", resource_status, teacher_li_id,
                    )
                    if resource_status != "draft":
                        review_status = {
                            "approved": "approved",
                            "pending_review": "pending",
                            "rejected": "rejected",
                        }[resource_status]
                        upsert_resource_review(
                            cur,
                            rid,
                            teacher_li_id,
                            teacher_li_id,
                            review_status,
                        )
                    for kp_id in kps_subset[:2]:
                        evidence = chunk_by_kp[kp_id]
                        upsert_resource_evidence(
                            cur,
                            rid,
                            evidence["chunk_id"],
                            kp_id,
                            evidence["content"],
                            resource_status,
                            teacher_li_id,
                            evidence["source_page"],
                        )
                    log.info(
                        "  resource %s (id=%s, status=%s, evidence=%d)",
                        title,
                        rid,
                        resource_status,
                        min(2, len(kps_subset)),
                    )

            log.info("=== learning feedbacks ===")
            for (uname, code), pid in profile_ids.items():
                student_id = member_user_ids[uname]
                # Three complementary signals drive analytics and mastery updates.
                for i in range(3):
                    rid = fetchone(cur, "SELECT resource_id FROM learning_resources WHERE course_id=%s LIMIT 1",
                                    course_ids[code])
                    resource_id = rid["resource_id"] if rid else None
                    ftype = ["quiz_result", "self_report", "study_note"][i]
                    score = round(random.uniform(0.55, 0.95), 3) if ftype == "quiz_result" else None
                    sm = round(random.uniform(0.5, 0.9), 3) if ftype in ("self_report", "study_note") else None
                    diff = random.choice(["appropriate", "too_hard", "appropriate"])
                    content = {
                        "quiz_result": f"第 {i+1} 次测验正确率 {int((score or 0)*100)}%",
                        "self_report": "我觉得这一节讲得清楚，例题有帮助。",
                        "study_note": "整理了关键概念、错题原因和下一步练习计划。",
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
        log.info("=" * 60)
    except Exception as exc:
        conn.rollback()
        log.exception(
            "Seed failed, transaction rolled back (%s).", type(exc).__name__
        )
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
