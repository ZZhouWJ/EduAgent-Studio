"""学习服务 — 课程、知识点、学习任务"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import random

_MOCK_COURSES = [
    {
        "id": 1,
        "name": "数据库系统原理",
        "code": "CS201",
        "description": "系统学习关系型数据库理论、SQL语言、事务管理与数据库设计。",
        "teacher": "张教授",
        "semester": "2025-2026学年春季学期",
        "status": "active",
        "knowledge_point_count": 14,
        "student_count": 156,
        "task_count": 12,
        "cover_color": "#409eff",
        "tags": ["核心课", "数据库", "理论"],
        "knowledge_points": [
            {"id": 1, "name": "关系模型基础", "mastery_avg": 0.75, "difficulty": "基础"},
            {"id": 2, "name": "SQL基本查询", "mastery_avg": 0.85, "difficulty": "基础"},
            {"id": 3, "name": "数据定义DDL", "mastery_avg": 0.78, "difficulty": "基础"},
            {"id": 4, "name": "索引与优化", "mastery_avg": 0.55, "difficulty": "进阶"},
            {"id": 5, "name": "SQL多表连接", "mastery_avg": 0.30, "difficulty": "进阶"},
            {"id": 6, "name": "子查询与视图", "mastery_avg": 0.52, "difficulty": "进阶"},
            {"id": 7, "name": "数据库设计范式", "mastery_avg": 0.48, "difficulty": "进阶"},
            {"id": 8, "name": "事务隔离级别", "mastery_avg": 0.20, "difficulty": "高级"},
            {"id": 9, "name": "并发控制与锁", "mastery_avg": 0.25, "difficulty": "高级"},
            {"id": 10, "name": "数据库恢复技术", "mastery_avg": 0.35, "difficulty": "高级"},
            {"id": 11, "name": "NoSQL与NewSQL", "mastery_avg": 0.40, "difficulty": "高级"},
            {"id": 12, "name": "数据库范式", "mastery_avg": 0.40, "difficulty": "进阶"},
            {"id": 13, "name": "查询优化器", "mastery_avg": 0.18, "difficulty": "高级"},
            {"id": 14, "name": "数据库安全", "mastery_avg": 0.45, "difficulty": "进阶"},
        ]
    },
    {
        "id": 2,
        "name": "Python程序设计",
        "code": "CS102",
        "description": "Python语言基础、函数式编程、面向对象与常用标准库实践。",
        "teacher": "李老师",
        "semester": "2025-2026学年春季学期",
        "status": "active",
        "knowledge_point_count": 10,
        "student_count": 203,
        "task_count": 10,
        "cover_color": "#67c23a",
        "tags": ["编程基础", "Python"],
        "knowledge_points": [
            {"id": 20, "name": "Python基础语法", "mastery_avg": 0.72, "difficulty": "基础"},
            {"id": 21, "name": "函数参数传递", "mastery_avg": 0.45, "difficulty": "进阶"},
            {"id": 22, "name": "模块导入", "mastery_avg": 0.38, "difficulty": "进阶"},
            {"id": 23, "name": "异常处理", "mastery_avg": 0.42, "difficulty": "进阶"},
            {"id": 24, "name": "文件操作", "mastery_avg": 0.55, "difficulty": "基础"},
            {"id": 25, "name": "面向对象编程", "mastery_avg": 0.35, "difficulty": "进阶"},
            {"id": 26, "name": "装饰器与元编程", "mastery_avg": 0.20, "difficulty": "高级"},
            {"id": 27, "name": "并发编程", "mastery_avg": 0.25, "difficulty": "高级"},
            {"id": 28, "name": "网络编程", "mastery_avg": 0.30, "difficulty": "进阶"},
            {"id": 29, "name": "数据分析基础", "mastery_avg": 0.40, "difficulty": "进阶"},
        ]
    },
    {
        "id": 3,
        "name": "软件工程实践",
        "code": "CS305",
        "description": "软件开发生命周期、敏捷方法、需求分析、设计模式与团队协作。",
        "teacher": "王教授",
        "semester": "2025-2026学年春季学期",
        "status": "active",
        "knowledge_point_count": 8,
        "student_count": 118,
        "task_count": 8,
        "cover_color": "#e6a23c",
        "tags": ["软工", "方法论", "实践"],
        "knowledge_points": [
            {"id": 30, "name": "需求分析", "mastery_avg": 0.60, "difficulty": "进阶"},
            {"id": 31, "name": "UML建模", "mastery_avg": 0.55, "difficulty": "进阶"},
            {"id": 32, "name": "架构设计", "mastery_avg": 0.40, "difficulty": "高级"},
            {"id": 33, "name": "设计模式", "mastery_avg": 0.35, "difficulty": "高级"},
            {"id": 34, "name": "敏捷开发", "mastery_avg": 0.65, "difficulty": "基础"},
            {"id": 35, "name": "测试策略", "mastery_avg": 0.50, "difficulty": "进阶"},
            {"id": 36, "name": "DevOps实践", "mastery_avg": 0.30, "difficulty": "高级"},
            {"id": 37, "name": "代码质量管理", "mastery_avg": 0.45, "difficulty": "进阶"},
        ]
    }
]

_TASK_STATUSES = ["pending", "in_progress", "submitted", "reviewed", "completed"]
_TASK_TYPES = ["lecture", "exercise", "quiz", "project", "review"]
_PRIORITIES = ["low", "medium", "high"]

_MOCK_TASKS = [
    {"id": 1, "course_id": 1, "title": "数据库系统基础理论测试", "type": "quiz", "status": "completed", "priority": "high", "due_date": "2026-04-10", "description": "涵盖关系模型、SQL基础、事务ACID特性的综合测验。", "student_count": 156, "completion_rate": 0.92},
    {"id": 2, "course_id": 1, "title": "SQL多表连接练习", "type": "exercise", "status": "in_progress", "priority": "high", "due_date": "2026-06-15", "description": "练习 INNER JOIN、LEFT JOIN、RIGHT JOIN、FULL OUTER JOIN 等多表连接操作。", "student_count": 156, "completion_rate": 0.45},
    {"id": 3, "course_id": 1, "title": "数据库设计大作业", "type": "project", "status": "pending", "priority": "high", "due_date": "2026-06-30", "description": "完成一个完整数据库系统的设计、实现与文档撰写。", "student_count": 156, "completion_rate": 0.0},
    {"id": 4, "course_id": 1, "title": "事务与并发控制实验", "type": "exercise", "status": "completed", "priority": "medium", "due_date": "2026-05-20", "description": "验证脏读、不可重复读、幻读现象，理解 MVCC 机制。", "student_count": 156, "completion_rate": 0.88},
    {"id": 5, "course_id": 1, "title": "索引优化专题讲义生成", "type": "lecture", "status": "in_progress", "priority": "medium", "due_date": "2026-06-20", "description": "生成 B+Tree 索引原理与 SQL 优化的个性化讲义。", "student_count": 156, "completion_rate": 0.60},
    {"id": 6, "course_id": 2, "title": "Python函数式编程练习", "type": "exercise", "status": "completed", "priority": "medium", "due_date": "2026-05-15", "description": "练习 map、filter、reduce、lambda 等函数式编程技巧。", "student_count": 203, "completion_rate": 0.85},
    {"id": 7, "course_id": 2, "title": "面向对象综合项目", "type": "project", "status": "in_progress", "priority": "high", "due_date": "2026-06-25", "description": "设计一个使用继承、封装、多态的完整学生管理系统。", "student_count": 203, "completion_rate": 0.35},
    {"id": 8, "course_id": 2, "title": "Python异常处理测试", "type": "quiz", "status": "completed", "priority": "low", "due_date": "2026-04-25", "description": "Python 异常捕获、自定义异常、异常链的掌握度测验。", "student_count": 203, "completion_rate": 0.90},
    {"id": 9, "course_id": 3, "title": "UML建模作业", "type": "exercise", "status": "pending", "priority": "medium", "due_date": "2026-06-18", "description": "为选定的业务场景绘制用例图、类图、时序图。", "student_count": 118, "completion_rate": 0.0},
    {"id": 10, "course_id": 3, "title": "敏捷开发团队项目", "type": "project", "status": "in_progress", "priority": "high", "due_date": "2026-07-05", "description": "以 Scrum 方式完成一个完整的软件产品迭代开发。", "student_count": 118, "completion_rate": 0.55},
]


class LearningService:
    def list_courses(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": _MOCK_COURSES}

    def get_course(self, course_id: int) -> Dict[str, Any]:
        for course in _MOCK_COURSES:
            if course["id"] == course_id:
                return {"code": 0, "message": "success", "data": course}
        return {"code": 404, "message": "课程不存在", "data": None}

    def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: int = None,
        status: str = None,
    ) -> Dict[str, Any]:
        items = list(_MOCK_TASKS)
        if course_id is not None:
            items = [t for t in items if t["course_id"] == course_id]
        if status:
            items = [t for t in items if t["status"] == status]

        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]

        for item in page_items:
            course = next((c for c in _MOCK_COURSES if c["id"] == item["course_id"]), None)
            item["course_name"] = course["name"] if course else ""

        return {
            "code": 0,
            "message": "success",
            "data": {"items": page_items, "total": total, "page": page, "page_size": page_size}
        }

    def get_task(self, task_id: int) -> Dict[str, Any]:
        for task in _MOCK_TASKS:
            if task["id"] == task_id:
                course = next((c for c in _MOCK_COURSES if c["id"] == task["course_id"]), None)
                result = dict(task)
                result["course_name"] = course["name"] if course else ""
                result["course_description"] = course["description"] if course else ""
                return {"code": 0, "message": "success", "data": result}
        return {"code": 404, "message": "任务不存在", "data": None}
