"""学生画像 Service"""
from typing import Any, Dict, List, Optional

_MOCK_PROFILES = [
    {
        "profile_id": 1,
        "student_id": 101,
        "student_name": "李明",
        "course_id": 1,
        "course_name": "数据库系统原理",
        "learning_goal": "掌握数据库系统原理，能够独立完成数据库设计",
        "current_level": "大二计算机专业，已学习SQL基础",
        "weak_points": ["SQL多表连接", "事务隔离级别", "数据库范式"],
        "preferences": ["图文讲义", "案例分析"],
        "mastery_score": 0.42,
        "last_updated": "2026-06-10",
        "student_no": "2023001234",
        "interests": ["后端开发", "数据工程"],
        "resource_preferences": ["讲义", "案例"],
        "weekly_hours": 8,
        "ai_suggestions": "建议优先攻克SQL多表连接，可通过教务系统真实数据练习",
        "strong_points": [
            {"kp_id": 2, "kp_name": "SQL基本查询", "mastery": 0.85},
            {"kp_id": 3, "kp_name": "数据定义DDL", "mastery": 0.78}
        ],
        "recent_tasks": [
            {"task_id": 10, "title": "数据库事务与并发控制", "status": "completed", "completed_at": "2026-06-09"},
            {"task_id": 11, "title": "SQL多表连接练习", "status": "in_progress", "completed_at": ""}
        ],
        "recent_tests": [
            {"test_id": 5, "accuracy": 0.70, "date": "2026-06-08"},
            {"test_id": 4, "accuracy": 0.65, "date": "2026-06-05"}
        ]
    },
    {
        "profile_id": 2,
        "student_id": 102,
        "student_name": "王悦",
        "course_id": 1,
        "course_name": "数据库系统原理",
        "learning_goal": "深入理解数据库内核机制",
        "current_level": "大三学生，有一定数据库基础",
        "weak_points": ["索引优化", "查询计划分析"],
        "preferences": ["深度技术文章", "源码分析"],
        "mastery_score": 0.68,
        "last_updated": "2026-06-09",
        "student_no": "2022005678",
        "interests": ["数据库内核", "性能优化"],
        "resource_preferences": ["技术文章", "源码"],
        "weekly_hours": 12,
        "ai_suggestions": "建议深入学习索引结构和查询优化器原理",
        "strong_points": [],
        "recent_tasks": [],
        "recent_tests": []
    },
    {
        "profile_id": 3,
        "student_id": 103,
        "student_name": "陈思雨",
        "course_id": 2,
        "course_name": "Python程序设计",
        "learning_goal": "掌握Python编程，能够开发实用工具",
        "current_level": "大一学生，零基础入门",
        "weak_points": ["函数参数传递", "模块导入", "异常处理"],
        "preferences": ["视频教程", "手把手练习"],
        "mastery_score": 0.35,
        "last_updated": "2026-06-07",
        "student_no": "2023012345",
        "interests": ["Web开发", "自动化脚本"],
        "resource_preferences": ["视频", "练习题"],
        "weekly_hours": 6,
        "ai_suggestions": "建议从基础语法入手，多做小项目练习",
        "strong_points": [{"kp_id": 20, "kp_name": "Python基础语法", "mastery": 0.72}],
        "recent_tasks": [],
        "recent_tests": []
    }
]


class ProfileService:
    """学生画像 Service"""

    def list_profiles(
        self,
        user: Any,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取学生画像列表"""
        items = _MOCK_PROFILES.copy()
        if course_id:
            items = [p for p in items if p["course_id"] == course_id]
        if keyword:
            items = [
                p for p in items
                if keyword.lower() in p["student_name"].lower() or keyword.lower() in p.get("student_no", "").lower()
            ]
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": items[start:end],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        }

    def get_profile(self, profile_id: int, user: Any) -> Dict[str, Any]:
        """获取学生画像详情"""
        for p in _MOCK_PROFILES:
            if p["profile_id"] == profile_id:
                return {"code": 0, "message": "success", "data": p}
        return {"code": 404, "message": "画像不存在", "data": None}

    def update_profile(self, profile_id: int, data: Dict[str, Any], user: Any) -> Dict[str, Any]:
        """更新学生画像"""
        for p in _MOCK_PROFILES:
            if p["profile_id"] == profile_id:
                p.update(data)
                p["last_updated"] = "2026-06-11"
                return {"code": 0, "message": "更新成功", "data": p}
        return {"code": 404, "message": "画像不存在", "data": None}

    def update_mastery(self, profile_id: int, data: Dict[str, Any], user: Any) -> Dict[str, Any]:
        """更新知识点掌握度"""
        for p in _MOCK_PROFILES:
            if p["profile_id"] == profile_id:
                p["last_updated"] = "2026-06-11"
                return {"code": 0, "message": "掌握度更新成功", "data": {"kp_id": data.get("kp_id"), "new_mastery": data.get("mastery")}}
        return {"code": 404, "message": "画像不存在", "data": None}
