"""
学习模块 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
软删除为主，不物理删除。

Tables:
- courses: course_id, course_name, course_code, description, teacher_id, status, is_deleted, created_at, updated_at
- knowledge_points: kp_id, course_id, kp_name, kp_code, parent_kp_id, difficulty_level, description, estimated_hours, is_deleted, created_at, updated_at
- learning_tasks: task_id, course_id, title, description, target_kp_ids, creator_id, assignee_id, status, due_date, is_deleted, created_at, updated_at
- users: user_id, username, real_name (teacher name)
- student_profiles: profile_id, student_id, course_id, is_deleted
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_db_cursor

COVER_COLORS = ["#409eff", "#67c23a", "#e6a23c", "#f56c6c", "#909399"]

DIFFICULTY_MAP = {
    "basic": "基础",
    "intermediate": "进阶",
    "advanced": "高级",
}


def _compute_cover_color(course_id: int) -> str:
    """根据 course_id 循环选择封面颜色。"""
    return COVER_COLORS[course_id % len(COVER_COLORS)]


def _map_difficulty(level: Optional[str]) -> str:
    """将 difficulty_level 映射为中文标签。"""
    if not level:
        return "基础"
    return DIFFICULTY_MAP.get(level.lower(), "基础")


def _current_semester(reference: Optional[datetime] = None) -> str:
    current = reference or datetime.now()
    if current.month >= 9:
        return f"{current.year}-{current.year + 1}学年秋季学期"
    academic_year = current.year - 1
    term = "春季学期" if current.month >= 2 else "秋季学期"
    return f"{academic_year}-{current.year}学年{term}"


class LearningRepository:
    """学习模块数据访问层。"""

    def list_courses(self, course_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Returns list of course dicts with knowledge_points embedded."""
        if course_ids == []:
            return []

        course_filter = ""
        params: List[Any] = []
        if course_ids is not None:
            placeholders = ",".join(["%s"] * len(course_ids))
            course_filter = f" AND c.course_id IN ({placeholders})"
            params.extend(course_ids)

        sql = """
            SELECT
                c.course_id,
                c.course_name,
                c.course_code,
                c.description,
                c.status,
                u.real_name AS teacher,
                COALESCE(kp_stats.kp_count, 0) AS kp_count,
                COALESCE(profile_stats.student_count, 0) AS student_count,
                COALESCE(profile_stats.mastery_avg, 0) AS mastery_avg,
                COALESCE(task_stats.task_count, 0) AS task_count,
                COALESCE(resource_stats.resource_count, 0) AS resource_count
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.user_id AND u.is_deleted = 0
            LEFT JOIN (
                SELECT course_id, COUNT(*) AS kp_count
                FROM knowledge_points WHERE is_deleted = 0 GROUP BY course_id
            ) kp_stats ON kp_stats.course_id = c.course_id
            LEFT JOIN (
                SELECT course_id, COUNT(*) AS student_count,
                       AVG(mastery_score) AS mastery_avg
                FROM student_profiles WHERE is_deleted = 0 GROUP BY course_id
            ) profile_stats ON profile_stats.course_id = c.course_id
            LEFT JOIN (
                SELECT course_id, COUNT(*) AS task_count
                FROM learning_tasks WHERE is_deleted = 0 GROUP BY course_id
            ) task_stats ON task_stats.course_id = c.course_id
            LEFT JOIN (
                SELECT course_id, COUNT(*) AS resource_count
                FROM learning_resources WHERE is_deleted = 0 GROUP BY course_id
            ) resource_stats ON resource_stats.course_id = c.course_id
            WHERE c.is_deleted = 0
        """ + course_filter + """
            ORDER BY c.course_id ASC
        """

        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            courses = cursor.fetchall()

            knowledge_points_by_course: Dict[int, List[Dict[str, Any]]] = {
                int(course["course_id"]): [] for course in courses
            }
            if courses:
                returned_ids = list(knowledge_points_by_course)
                placeholders = ",".join(["%s"] * len(returned_ids))
                cursor.execute(
                    f"""
                    SELECT kp.course_id, kp.kp_id, kp.kp_name, kp.difficulty_level,
                           COALESCE(AVG(mastery.mastery_level), 0) AS mastery_avg
                    FROM knowledge_points kp
                    LEFT JOIN student_knowledge_mastery mastery
                      ON mastery.kp_id = kp.kp_id AND mastery.is_deleted = 0
                    WHERE kp.course_id IN ({placeholders}) AND kp.is_deleted = 0
                    GROUP BY kp.course_id, kp.kp_id, kp.kp_name, kp.difficulty_level
                    ORDER BY kp.course_id, kp.kp_id
                    """,
                    returned_ids,
                )
                for row in cursor.fetchall():
                    knowledge_points_by_course[int(row["course_id"])].append({
                        "id": row["kp_id"],
                        "name": row["kp_name"],
                        "mastery_avg": float(row["mastery_avg"]),
                        "difficulty": _map_difficulty(row["difficulty_level"]),
                    })

        result = []
        semester = _current_semester()
        for course in courses:
            course_id = int(course["course_id"])
            result.append({
                "id": course_id,
                "name": course["course_name"],
                "code": course["course_code"],
                "description": course["description"],
                "teacher": course["teacher"] or "",
                "semester": semester,
                "status": course["status"],
                "knowledge_point_count": int(course["kp_count"]),
                "student_count": int(course["student_count"]),
                "task_count": int(course["task_count"]),
                "resource_count": int(course["resource_count"]),
                "mastery_avg": float(course["mastery_avg"]),
                "cover_color": _compute_cover_color(course_id),
                "tags": [],
                "knowledge_points": knowledge_points_by_course[course_id],
            })

        return result

    def get_course(self, course_id: int, profile_id: int = None) -> Optional[Dict[str, Any]]:
        """Returns single course dict with full knowledge_points list.
        
        Args:
            course_id: 课程 ID
            profile_id: 学生画像 ID（用于查询该学生的知识点掌握度）
        """
        sql = """
            SELECT
                c.course_id,
                c.course_name,
                c.course_code,
                c.description,
                c.status,
                u.real_name AS teacher
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.user_id AND u.is_deleted = 0
            WHERE c.course_id = %s AND c.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (course_id,))
            course = cursor.fetchone()

        if not course:
            return None

        kp_sql = """
            SELECT
                kp.kp_id,
                kp.kp_name,
                kp.difficulty_level,
                COALESCE(skm.mastery_level, 0.5) AS mastery_level
            FROM knowledge_points kp
            LEFT JOIN student_knowledge_mastery skm
                ON kp.kp_id = skm.kp_id
                AND skm.profile_id = %s
                AND skm.is_deleted = 0
            WHERE kp.course_id = %s AND kp.is_deleted = 0
            ORDER BY kp.kp_id ASC
        """
        with get_db_cursor() as cursor:
            cursor.execute(kp_sql, (profile_id, course_id))
            kp_rows = cursor.fetchall()
            knowledge_points = [
                {
                    "id": row["kp_id"],
                    "name": row["kp_name"],
                    "mastery_level": row["mastery_level"],
                    "mastery_avg": row["mastery_level"],
                    "difficulty": _map_difficulty(row["difficulty_level"]),
                }
                for row in kp_rows
            ]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM knowledge_points WHERE course_id = %s AND is_deleted = 0",
                (course_id,),
            )
            kp_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM student_profiles WHERE course_id = %s AND is_deleted = 0",
                (course_id,),
            )
            student_count = cursor.fetchone()["cnt"]

            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM learning_tasks WHERE course_id = %s AND is_deleted = 0",
                (course_id,),
            )
            task_count = cursor.fetchone()["cnt"]

        return {
            "id": course["course_id"],
            "name": course["course_name"],
            "code": course["course_code"],
            "description": course["description"],
            "teacher": course["teacher"] or "",
            "semester": "2025-2026学年春季学期",
            "status": course["status"],
            "knowledge_point_count": kp_count,
            "student_count": student_count,
            "task_count": task_count,
            "cover_color": _compute_cover_color(course["course_id"]),
            "tags": [],
            "knowledge_points": knowledge_points,
        }

    def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        course_ids: Optional[List[int]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns paginated task list:
        {
            "items": [{id, course_id, course_name, title, type, status, priority, due_date, description, student_count: 0, completion_rate: 0.0}, ...],
            "total": int,
            "page": int,
            "page_size": int
        }
        type comes from task title keyword detection (exercise/quiz/project/lecture/review), default "exercise"
        priority from due_date proximity (high if <7 days, medium if <14 days, else low)
        """
        offset = (page - 1) * page_size

        filters = ["t.is_deleted = 0"]
        params: List[Any] = []

        if course_id is not None:
            filters.append("t.course_id = %s")
            params.append(course_id)
        elif course_ids == []:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
            }
        elif course_ids is not None:
            placeholders = ",".join(["%s"] * len(course_ids))
            filters.append(f"t.course_id IN ({placeholders})")
            params.extend(course_ids)
        if status:
            filters.append("t.status = %s")
            params.append(status)

        where_clause = " AND ".join(filters)

        with get_db_cursor() as cursor:
            count_sql = f"SELECT COUNT(*) AS total FROM learning_tasks t WHERE {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"]

            data_sql = f"""
                SELECT
                    t.task_id,
                    t.course_id,
                    t.title,
                    t.description,
                    t.status,
                    t.due_date,
                    c.course_name
                FROM learning_tasks t
                INNER JOIN courses c ON t.course_id = c.course_id AND c.is_deleted = 0
                WHERE {where_clause}
                ORDER BY t.task_id ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(data_sql, params + [page_size, offset])
            rows = cursor.fetchall()

        now = datetime.now()
        items = []
        for row in rows:
            due_date = row["due_date"]
            priority = self._compute_priority(due_date, now)
            task_type = self._detect_task_type(row["title"])

            items.append(
                {
                    "id": row["task_id"],
                    "course_id": row["course_id"],
                    "course_name": row["course_name"],
                    "title": row["title"],
                    "type": task_type,
                    "status": row["status"],
                    "priority": priority,
                    "due_date": row["due_date"].strftime("%Y-%m-%d") if isinstance(due_date, datetime) else str(due_date),
                    "description": row["description"] or "",
                    "student_count": 0,
                    "completion_rate": 0.0,
                }
            )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Returns single task dict with course_name, course_description."""
        sql = """
            SELECT
                t.task_id,
                t.course_id,
                t.title,
                t.description,
                t.status,
                t.due_date,
                c.course_name,
                c.description AS course_description
            FROM learning_tasks t
            INNER JOIN courses c ON t.course_id = c.course_id AND c.is_deleted = 0
            WHERE t.task_id = %s AND t.is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(sql, (task_id,))
            row = cursor.fetchone()

        if not row:
            return None

        due_date = row["due_date"]
        now = datetime.now()
        priority = self._compute_priority(due_date, now)
        task_type = self._detect_task_type(row["title"])

        return {
            "id": row["task_id"],
            "course_id": row["course_id"],
            "course_name": row["course_name"],
            "course_description": row["course_description"] or "",
            "title": row["title"],
            "type": task_type,
            "status": row["status"],
            "priority": priority,
            "due_date": row["due_date"].strftime("%Y-%m-%d") if isinstance(due_date, datetime) else str(due_date),
            "description": row["description"] or "",
            "student_count": 0,
            "completion_rate": 0.0,
        }

    def create_task(
        self,
        course_id: int,
        title: str,
        description: Optional[str] = None,
        target_kp_ids: Optional[List[int]] = None,
        assignee_id: Optional[int] = None,
        due_date: Optional[str] = None,
        creator_id: int = 0,
    ) -> Dict[str, Any]:
        """创建学习任务。"""
        kp_str = ",".join(str(k) for k in target_kp_ids) if target_kp_ids else None
        due_dt = due_date if due_date else None
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO learning_tasks
                    (course_id, title, description, target_kp_ids, assignee_id, due_date, creator_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'assigned', NOW(), NOW())
                """,
                (course_id, title, description, kp_str, assignee_id, due_dt, creator_id),
            )
            task_id = cursor.lastrowid
        return self.get_task(task_id) or {"id": task_id, "course_id": course_id, "title": title}

    @staticmethod
    def _detect_task_type(title: str) -> str:
        """根据标题关键词检测任务类型。"""
        title_lower = title.lower()
        if "练习" in title or "exercise" in title_lower or "作业" in title:
            return "exercise"
        if "测验" in title or "quiz" in title_lower or "测试" in title:
            return "quiz"
        if "项目" in title or "project" in title_lower or "大作业" in title:
            return "project"
        if "讲义" in title or "lecture" in title_lower or "课程" in title:
            return "lecture"
        if "复习" in title or "review" in title_lower:
            return "review"
        return "exercise"

    @staticmethod
    def _compute_priority(due_date, now: datetime) -> str:
        """根据截止日期距离判断优先级。"""
        if due_date is None:
            return "low"
        if isinstance(due_date, str):
            try:
                due_date = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                return "low"
        delta_days = (due_date - now).days
        if delta_days < 7:
            return "high"
        if delta_days < 14:
            return "medium"
        return "low"

    def get_learning_path(self, course_id: int, profile_id: Optional[int] = None) -> Dict[str, Any]:
        """
        构建课程知识点学习路径图谱（用于 ECharts graph 可视化）。

        图谱结构：
        - nodes: 知识点节点，含 mastery_level / difficulty_level
        - edges: 依赖关系（parent_kp_id → child kp_id）
        - summary: 整体统计

        若传入 profile_id，则查询该学生的掌握度；否则只返回课程知识点结构。
        """
        with get_db_cursor() as cursor:
            # 查询课程所有知识点（按 parent 层级排序）
            cursor.execute("""
                SELECT
                    kp.kp_id,
                    kp.kp_name,
                    kp.kp_code,
                    kp.parent_kp_id,
                    kp.difficulty_level,
                    kp.description,
                    kp.estimated_hours,
                    COALESCE(skm.mastery_level, 0.5) AS mastery_level,
                    skm.last_test_score,
                    skm.last_test_date
                FROM knowledge_points kp
                LEFT JOIN student_knowledge_mastery skm
                    ON kp.kp_id = skm.kp_id
                    AND skm.profile_id = %s
                    AND skm.is_deleted = 0
                WHERE kp.course_id = %s AND kp.is_deleted = 0
                ORDER BY kp.parent_kp_id ASC, kp.kp_id ASC
            """, (profile_id, course_id))
            rows = cursor.fetchall()

        if not rows:
            return {"nodes": [], "edges": [], "summary": {"total": 0, "mastered": 0, "weak": 0}}

        # 构建节点和边
        nodes = []
        edges = []
        mastered = 0
        weak = 0
        found_current = False

        for row in rows:
            mastery = float(row["mastery_level"])
            if mastery >= 0.7:
                mastered += 1
            elif mastery < 0.5:
                weak += 1

            # 节点颜色：掌握（绿）/ 薄弱（红）/ 一般（橙）
            if mastery >= 0.7:
                node_color = "#67c23a"  # 绿色
                status_label = "已掌握"
            elif mastery < 0.4:
                node_color = "#f56c6c"  # 红色
                status_label = "薄弱"
            elif mastery < 0.7:
                node_color = "#e6a23c"  # 橙色
                status_label = "学习中"
            else:
                node_color = "#909399"
                status_label = "未学习"

            # 第一个非"已掌握"的节点标记为"当前学习点"
            if not found_current and status_label != "已掌握":
                status_label = "当前学习点"
                node_color = "#2563eb"  # 蓝色高亮
                found_current = True

            # 节点大小按难度和掌握度调整
            size_base = 60
            diff_map = {"basic": 1, "intermediate": 2, "advanced": 3}
            diff_val = diff_map.get(row["difficulty_level"] or "basic", 1)
            node_size = size_base + diff_val * 10

            nodes.append({
                "id": row["kp_id"],
                "kp_id": row["kp_id"],
                "name": row["kp_name"],
                "kp_name": row["kp_name"],
                "kp_code": row["kp_code"],
                "difficulty_level": row["difficulty_level"],
                "description": row["description"],
                "estimated_hours": row["estimated_hours"],
                "mastery_level": mastery,
                "last_test_score": row["last_test_score"],
                "last_test_date": str(row["last_test_date"]) if row["last_test_date"] else None,
                "status_label": status_label,
                "color": node_color,
                "size": node_size,
            })

            # 边（依赖关系）
            parent_id = row["parent_kp_id"]
            if parent_id:
                edges.append({
                    "source": parent_id,
                    "target": row["kp_id"],
                    "label": "前置",
                })

        # 计算平均掌握度
        avg_mastery = sum(n["mastery_level"] for n in nodes) / len(nodes) if nodes else 0

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "total": len(nodes),
                "mastered": mastered,
                "weak": weak,
                "avg_mastery": round(avg_mastery, 3),
                "profile_id": profile_id,
                "course_id": course_id,
            },
        }

    def update_course_status(self, course_id: int, status: str) -> Optional[Dict[str, Any]]:
        """更新课程状态。返回更新后的课程 dict 或 None（不存在）。"""
        allowed = {"active", "archived", "draft"}
        if status not in allowed:
            raise ValueError(f"Invalid status: {status}. Must be one of {allowed}.")

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE courses SET status=%s, updated_at=NOW() WHERE course_id=%s AND is_deleted=0",
                (status, course_id),
            )
            if cursor.rowcount == 0:
                return None
            cursor.execute(
                "SELECT course_id, course_name, course_code, status FROM courses WHERE course_id=%s",
                (course_id,),
            )
            return dict(cursor.fetchone())

    def get_recommended_resources(
        self,
        profile_id: int,
        course_id: int,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        获取推荐资源。

        排序逻辑:
        1. 关联低 mastery 知识点的资源优先
        2. 匹配学生资源偏好类型
        3. 排除已学过的资源(查 learning_feedbacks)
        4. 只取审核通过(approved)的资源

        Returns:
            List of resource dicts with resource_id, title, type, reason, etc.
        """
        with get_db_cursor() as cursor:
            # 获取学生资源偏好
            cursor.execute(
                "SELECT resource_preferences FROM student_profiles WHERE profile_id = %s AND is_deleted = 0",
                (profile_id,),
            )
            pref_row = cursor.fetchone()
            resource_prefs = pref_row["resource_preferences"].split(",") if pref_row and pref_row["resource_preferences"] else []

            # 获取低 mastery 知识点（< 0.5）
            cursor.execute("""
                SELECT kp.kp_id, kp.kp_name, skm.mastery_level
                FROM student_knowledge_mastery skm
                INNER JOIN knowledge_points kp ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                WHERE skm.profile_id = %s
                  AND skm.is_deleted = 0
                  AND skm.mastery_level < 0.5
                ORDER BY skm.mastery_level ASC
            """, (profile_id,))
            low_mastery_kps = cursor.fetchall()

            # 如果没有低 mastery 知识点，取所有知识点按 mastery 排序
            if not low_mastery_kps:
                cursor.execute("""
                    SELECT kp.kp_id, kp.kp_name, COALESCE(skm.mastery_level, 0.5) AS mastery_level
                    FROM knowledge_points kp
                    LEFT JOIN student_knowledge_mastery skm
                        ON kp.kp_id = skm.kp_id AND skm.profile_id = %s AND skm.is_deleted = 0
                    WHERE kp.course_id = %s AND kp.is_deleted = 0
                    ORDER BY mastery_level ASC
                """, (profile_id, course_id))
                low_mastery_kps = cursor.fetchall()

            kp_ids = [row["kp_id"] for row in low_mastery_kps]
            kp_names_map = {row["kp_id"]: row["kp_name"] for row in low_mastery_kps}

            # 已学过的资源 ID（通过 feedback）
            cursor.execute("""
                SELECT DISTINCT resource_id
                FROM learning_feedbacks
                WHERE profile_id = %s AND resource_id IS NOT NULL AND is_deleted = 0
            """, (profile_id,))
            learned_resource_ids = [row["resource_id"] for row in cursor.fetchall()]

        if not kp_ids:
            return []

        # 构建推荐资源查询
        # 资源关联的知识点包含低 mastery 知识点，且未学过，且审核通过
        placeholders_kp = ",".join(["%s"] * len(kp_ids))
        learned_ids_placeholder = ",".join(["%s"] * len(learned_resource_ids)) if learned_resource_ids else "'-1'"

        sql = f"""
            SELECT DISTINCT
                lr.resource_id,
                lr.resource_title,
                lr.resource_type,
                lr.difficulty,
                lr.target_kp_ids,
                lr.review_status,
                kp.kp_name AS primary_kp_name,
                kp.kp_id AS primary_kp_id,
                kp.estimated_hours,
                COALESCE(skm.mastery_level, 0.5) AS kp_mastery
            FROM learning_resources lr
            INNER JOIN knowledge_points kp ON lr.target_kp_ids LIKE CONCAT('%%', kp.kp_id, '%%')
            LEFT JOIN student_knowledge_mastery skm
                ON kp.kp_id = skm.kp_id AND skm.profile_id = %s AND skm.is_deleted = 0
            WHERE kp.kp_id IN ({placeholders_kp})
              AND lr.is_deleted = 0
              AND lr.review_status = 'approved'
              {'AND lr.resource_id NOT IN (' + learned_ids_placeholder + ')' if learned_resource_ids else ''}
            ORDER BY kp_mastery ASC, lr.created_at DESC
            LIMIT %s
        """

        params = [profile_id] + kp_ids + (learned_resource_ids if learned_resource_ids else []) + [limit]

        with get_db_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        # 构建推荐理由
        results = []
        for row in rows:
            # 解析 target_kp_ids
            target_kp_ids = []
            if row["target_kp_ids"]:
                target_kp_ids = [int(x.strip()) for x in row["target_kp_ids"].split(",") if x.strip()]

            # 找出该资源关联的最低 mastery 知识点
            min_mastery_kp_id = None
            min_mastery = 1.0
            for kp_id in target_kp_ids:
                if kp_id in kp_names_map:
                    cursor.execute("""
                        SELECT mastery_level FROM student_knowledge_mastery
                        WHERE profile_id = %s AND kp_id = %s AND is_deleted = 0
                    """, (profile_id, kp_id))
                    m_row = cursor.fetchone()
                    mastery = m_row["mastery_level"] if m_row else 0.5
                    if mastery < min_mastery:
                        min_mastery = mastery
                        min_mastery_kp_id = kp_id

            kp_name = kp_names_map.get(min_mastery_kp_id, row["primary_kp_name"]) if min_mastery_kp_id else row["primary_kp_name"]

            # 生成推荐理由
            if min_mastery < 0.3:
                reason = "巩固薄弱点"
            elif min_mastery < 0.5:
                reason = "加强易错点"
            else:
                reason = "复习已学内容"

            # 匹配偏好
            if resource_prefs and row["resource_type"] in resource_prefs:
                reason = f"推荐{row['resource_type']}类型资源，" + reason

            # estimated_minutes: 从知识点 estimated_hours 计算（小时 * 60）
            estimated_hours = row.get("estimated_hours") or 1
            estimated_minutes = round(float(estimated_hours) * 60)

            results.append({
                "resource_id": row["resource_id"],
                "title": row["resource_title"],
                "type": row["resource_type"],
                "difficulty": row.get("difficulty") or "basic",
                "reason": reason,
                "estimated_minutes": estimated_minutes,
                "kp_name": kp_name,
            })

        return results
