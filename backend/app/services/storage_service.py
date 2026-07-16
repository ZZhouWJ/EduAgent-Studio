"""存储服务模块

提供学习资源文件的存储、读取、列表和删除功能。
文件存储在 backend/storage/ 目录下，按 course_id/year_month/ 组织。
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

_storage_index: dict[str, Any] = {}
_index_loaded = False


def _get_data_dir() -> str:
    """获取数据目录路径（绝对路径）。"""
    data_dir = get_settings().app_data_dir
    if not os.path.isabs(data_dir):
        # 相对于 backend 目录解析为绝对路径
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_dir = os.path.join(backend_dir, data_dir)
    return os.path.abspath(data_dir)


def _get_storage_dir() -> str:
    """获取存储目录路径。"""
    return os.path.join(_get_data_dir(), "storage")


def _get_index_path() -> str:
    """获取索引文件路径。"""
    return os.path.join(_get_data_dir(), "storage_index.json")


def _ensure_directories() -> None:
    """确保存储目录和数据目录存在。"""
    os.makedirs(_get_storage_dir(), exist_ok=True)
    os.makedirs(_get_data_dir(), exist_ok=True)


def _load_index() -> None:
    """从磁盘加载索引文件。"""
    global _storage_index, _index_loaded
    if _index_loaded:
        return

    _ensure_directories()
    index_path = _get_index_path()

    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                _storage_index = json.load(f)
            logger.info("已加载存储索引，共 %d 条记录", len(_storage_index))
        except Exception as e:
            logger.warning("加载存储索引失败 (%s)，使用空索引", type(e).__name__)
            _storage_index = {}
    else:
        _storage_index = {}

    _index_loaded = True


def _save_index() -> None:
    """将索引保存到磁盘。"""
    _ensure_directories()
    index_path = _get_index_path()

    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(_storage_index, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存存储索引失败 (%s)", type(e).__name__)
        raise


def _get_year_month() -> str:
    """获取当前的年月字符串，格式为 YYYY-MM。"""
    return datetime.now().strftime("%Y-%m")


def save_resource_content(
    title: str,
    content: str,
    resource_type: str,
    course_id: int,
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    保存学习资源内容到存储系统。

    Args:
        title: 资源标题
        content: 资源内容（markdown 文本）
        resource_type: 资源类型（如 lecture, quiz, review 等）
        course_id: 课程 ID
        metadata: 附加元数据

    Returns:
        包含 file_id 和 url 的字典
    """
    _load_index()

    file_id = str(uuid.uuid4())
    year_month = _get_year_month()
    storage_dir = os.path.join(_get_storage_dir(), str(course_id), year_month)
    _ensure_directories()
    os.makedirs(storage_dir, exist_ok=True)  # 确保 course_id/year_month 目录存在

    file_data = {
        "title": title,
        "content": content,
        "resource_type": resource_type,
        "course_id": course_id,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat(),
    }

    file_path = os.path.join(storage_dir, f"{file_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(file_data, f, ensure_ascii=False, indent=2)

    url = f"/api/storage/{file_id}"

    _storage_index[file_id] = {
        "file_id": file_id,
        "title": title,
        "resource_type": resource_type,
        "course_id": course_id,
        "url": url,
        "file_path": file_path,
        "year_month": year_month,
        "created_at": file_data["created_at"],
        "deleted": False,
    }
    _save_index()

    logger.info("已保存资源: file_id=%s course_id=%d", file_id, course_id)

    return {
        "file_id": file_id,
        "url": url,
        "title": title,
        "resource_type": resource_type,
        "course_id": course_id,
        "created_at": file_data["created_at"],
    }


def get_resource_content(file_id: str) -> Optional[dict[str, Any]]:
    """
    根据 file_id 获取资源内容。

    Args:
        file_id: 资源文件 ID

    Returns:
        包含资源完整数据的字典，若不存在则返回 None
    """
    _load_index()

    if file_id not in _storage_index:
        return None

    entry = _storage_index[file_id]
    if entry.get("deleted"):
        return None

    file_path = entry.get("file_path")
    if not file_path or not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "file_id": file_id,
            **data,
            "url": entry.get("url"),
        }
    except Exception as e:
        logger.error("读取资源文件失败 (%s)", type(e).__name__)
        return None


def list_storage_files(
    course_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    分页列出存储文件。

    Args:
        course_id: 按课程 ID 过滤（可选）
        resource_type: 按资源类型过滤（可选）
        page: 页码（从 1 开始）
        page_size: 每页数量

    Returns:
        包含 items 和 total 的分页结果
    """
    _load_index()

    items = []
    for file_id, entry in _storage_index.items():
        if entry.get("deleted"):
            continue
        if course_id is not None and entry.get("course_id") != course_id:
            continue
        if resource_type and entry.get("resource_type") != resource_type:
            continue

        items.append({
            "file_id": file_id,
            "title": entry.get("title"),
            "resource_type": entry.get("resource_type"),
            "course_id": entry.get("course_id"),
            "url": entry.get("url"),
            "year_month": entry.get("year_month"),
            "created_at": entry.get("created_at"),
        })

    items.sort(key=lambda x: x["created_at"], reverse=True)

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]

    return {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def delete_storage_file(file_id: str) -> bool:
    """
    软删除存储文件。

    Args:
        file_id: 资源文件 ID

    Returns:
        是否删除成功
    """
    _load_index()

    if file_id not in _storage_index:
        return False

    _storage_index[file_id]["deleted"] = True
    _save_index()

    logger.info("已软删除资源: %s", file_id)
    return True


def get_storage_stats() -> dict[str, Any]:
    """
    获取存储统计信息。

    Returns:
        包含存储统计数据的字典
    """
    _load_index()

    total_files = 0
    total_courses = set()
    by_type: dict[str, int] = {}
    by_course: dict[int, int] = {}

    for file_id, entry in _storage_index.items():
        if entry.get("deleted"):
            continue

        total_files += 1
        course_id = entry.get("course_id")
        if course_id:
            total_courses.add(course_id)
            by_course[course_id] = by_course.get(course_id, 0) + 1

        resource_type = entry.get("resource_type", "unknown")
        by_type[resource_type] = by_type.get(resource_type, 0) + 1

    return {
        "total_files": total_files,
        "total_courses": len(total_courses),
        "by_type": by_type,
        "by_course": by_course,
    }
