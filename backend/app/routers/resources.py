"""学习资源 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.auth_service import get_current_user_dependency as get_current_user

router = APIRouter(prefix="/learning", tags=["学习资源"])

_MOCK_RESOURCES = [
    {
        "resource_id": 1,
        "course_id": 1,
        "course_name": "数据库系统原理",
        "resource_title": "SQL多表连接专题讲义（进阶）",
        "resource_type": "lecture",
        "difficulty": "intermediate",
        "status": "pending_review",
        "created_at": "2026-06-10T15:00:00"
    },
    {
        "resource_id": 2,
        "course_id": 1,
        "course_name": "数据库系统原理",
        "resource_title": "数据库范式复习计划",
        "resource_type": "review",
        "difficulty": "intermediate",
        "status": "approved",
        "created_at": "2026-06-09T10:00:00"
    },
    {
        "resource_id": 3,
        "course_id": 2,
        "course_name": "Python程序设计",
        "resource_title": "函数与模块练习题",
        "resource_type": "quiz",
        "difficulty": "basic",
        "status": "approved",
        "created_at": "2026-06-08T14:00:00"
    }
]


@router.get("/resources")
async def list_resources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    type: Optional[str] = None,
    token: str = Depends(get_current_user),
):
    items = _MOCK_RESOURCES.copy()
    if course_id:
        items = [r for r in items if r["course_id"] == course_id]
    if type:
        items = [r for r in items if r["resource_type"] == type]
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {"code": 0, "message": "success", "data": {"items": items[start:end], "total": total}}


@router.get("/resources/{resource_id}")
async def get_resource(
    resource_id: int,
    token: str = Depends(get_current_user),
):
    for r in _MOCK_RESOURCES:
        if r["resource_id"] == resource_id:
            # 补全详细内容（实际场景中从 DB 读取）
            detail = {
                **r,
                "content": _RESOURCE_CONTENTS.get(resource_id, ""),
                "target_kp_ids": _RESOURCE_KP_MAP.get(resource_id, []),
                "target_kp_names": _RESOURCE_KP_NAMES.get(resource_id, []),
                "generation_model": "deepseek-chat",
                "generation_agent": "resource_generation_agent",
                "status": r["status"],
                "reviewer_comment": None,
                "updated_at": r["created_at"],
                "version": 1,
            }
            return {"code": 0, "message": "success", "data": detail}
    return {"code": 404, "message": "资源不存在", "data": None}


# 资源正文内容（对应 resource_id）
_RESOURCE_CONTENTS = {
    1: """# SQL 多表连接专题讲义（进阶）

## 一、连接概述

连接（JOIN）是从两个或多个表中获取数据的操作。在关系数据库中，数据通常分布在多个相关表中，通过连接可以将它们组合在一起进行分析。

### 1.1 为什么需要连接？

假设有一个教务系统，students 表存储学生信息，scores 表存储成绩。如果想知道"每个学生的成绩"，就需要连接这两个表。

## 二、内连接（INNER JOIN）

内连接返回两个表中具有匹配值的记录。

### 语法
```sql
SELECT column_list
FROM table1
INNER JOIN table2 ON table1.column = table2.column;
```

### 示例
```sql
SELECT s.name, c.name AS class_name
FROM students s
INNER JOIN classes c ON s.class_id = c.id;
```

## 三、外连接（OUTER JOIN）

### 3.1 左外连接（LEFT JOIN）

返回左表中的所有记录，以及右表中匹配记录的记录。

```sql
SELECT s.name, sc.score
FROM students s
LEFT JOIN scores sc ON s.id = sc.student_id;
```

### 3.2 右外连接（RIGHT JOIN）

返回右表中的所有记录，以及左表中匹配记录的记录。

### 3.3 全外连接（FULL OUTER JOIN）

返回两个表的所有记录，匹配不上则为 NULL。

## 四、练习题

1. 查询所有学生的成绩，包括没有成绩的学生
2. 统计每个班级的平均分
3. 找出同时选修了"数据库"和"操作系统"两门课的学生

---
*本讲义由 EduAgent Studio 智能体工作台生成*
""",
    2: """# 数据库范式复习计划

## 复习目标
掌握数据库设计范式，能够识别并消除数据冗余。

## 每日任务
- Day 1: 第一范式（1NF）与第二范式（2NF）
- Day 2: 第三范式（3NF）与 BCNF
- Day 3: 综合练习与实际案例分析

---
*由 EduAgent Studio 生成*
""",
}

_RESOURCE_KP_MAP = {
    1: [5, 8],
    2: [12],
    3: [21, 22],
}

_RESOURCE_KP_NAMES = {
    1: ["SQL多表连接", "事务隔离级别"],
    2: ["数据库范式"],
    3: ["函数参数传递", "模块导入"],
}

