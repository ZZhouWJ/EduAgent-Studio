"""
Embedding 异步任务

- 批量计算知识点 embedding（调用 RAG 服务）
- 增量更新资源 embedding
- 定期重新计算全部 embedding
"""
import logging
from typing import Any, Dict, List

from app.celery_app import celery_app
from app.database import get_db_cursor

logger = logging.getLogger(__name__)


def _chunk_knowledge_point(kp: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks = []
    name = kp.get("kp_name", "")
    desc = kp.get("description") or ""
    difficulty = kp.get("difficulty_level") or ""

    chunk1 = f"知识点「{name}」，难度{difficulty}。"
    if desc:
        chunk1 += f" 简介：{desc[:200]}"
    chunks.append({"content_chunk": chunk1, "chunk_index": 0})

    parent_name = kp.get("parent_kp_name") or ""
    if parent_name:
        chunk2 = f"前置知识点「{parent_name}」是「{name}」的基础概念。"
        chunks.append({"content_chunk": chunk2, "chunk_index": 1})

    return chunks


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def compute_knowledge_point_embeddings(self, course_id: int) -> dict:
    """
    批量计算课程知识点的 embedding 向量。

    流程：
    1. 从 MySQL 读取课程知识点（含父知识点名称）
    2. 每个 KP 调用 RAG 服务生成 embedding 并存储到 pgvector
    """
    from app.services.rag_service import store_knowledge_point_embeddings

    logger.info(f"[Embedding] 开始计算课程 {course_id} 的知识点 embedding")
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    kp.kp_id,
                    kp.kp_name,
                    kp.description,
                    kp.difficulty_level,
                    pkp.kp_name AS parent_kp_name
                FROM knowledge_points kp
                LEFT JOIN knowledge_points pkp
                    ON kp.parent_kp_id = pkp.kp_id AND pkp.is_deleted = 0
                WHERE kp.course_id = %s AND kp.is_deleted = 0
                ORDER BY kp.kp_id ASC
            """, (course_id,))
            kp_rows = cursor.fetchall()

        if not kp_rows:
            logger.info(f"[Embedding] 课程 {course_id} 无知识点，跳过")
            return {"status": "success", "course_id": course_id, "processed": 0}

        results: List[Dict[str, Any]] = []
        for row in kp_rows:
            kp = dict(row)
            chunks = _chunk_knowledge_point(kp)
            result = store_knowledge_point_embeddings(kp["kp_id"], chunks)
            results.append({
                "kp_id": kp["kp_id"],
                "kp_name": kp["kp_name"],
                "chunks": len(chunks),
                "stored": result.get("stored", 0),
                "failed": result.get("failed", 0),
            })

        logger.info(
            f"[Embedding] 课程 {course_id} 完成，共处理 {len(results)} 个知识点"
        )
        return {
            "status": "success",
            "course_id": course_id,
            "processed_count": len(results),
            "details": results,
        }
    except Exception as e:
        logger.error(f"[Embedding] 计算失败: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def compute_resource_embedding(self, resource_id: int) -> dict:
    """
    为单个学习资源计算 embedding。

    流程：
    1. 从 MySQL 读取资源 content
    2. 按 500 字符滑动窗口切分
    3. 调用 RAG 服务生成 embedding 并存储到 pgvector
    """
    from app.services.rag_service import store_resource_embedding

    logger.info(f"[Embedding] 计算资源 {resource_id} 的 embedding")
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT content FROM learning_resources "
                "WHERE resource_id = %s AND is_deleted = 0",
                (resource_id,)
            )
            row = cursor.fetchone()

        if not row or not row.get("content"):
            logger.info(f"[Embedding] 资源 {resource_id} 无内容，跳过")
            return {"status": "skipped", "resource_id": resource_id}

        content = row["content"]
        result = store_resource_embedding(
            resource_id=resource_id,
            content=content,
            chunk_size=500,
        )

        logger.info(
            f"[Embedding] 资源 {resource_id} 完成，{result.get('stored', 0)} 个块已存储"
        )
        return {
            "status": "success",
            "resource_id": resource_id,
            "chunks": result.get("chunks", 0),
            "stored": result.get("stored", 0),
        }
    except Exception as e:
        logger.error(f"[Embedding] 资源 {resource_id} 计算失败: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def rebuild_all_embeddings(self) -> dict:
    """
    全量重建：遍历所有课程，重新计算所有知识点 embedding。
    """
    logger.info("[Embedding] 开始全量重建 embedding")
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT course_id FROM courses WHERE is_deleted = 0 ORDER BY course_id"
            )
            courses = cursor.fetchall()

        results = []
        for row in courses:
            course_id = row["course_id"]
            r = compute_knowledge_point_embeddings.delay(course_id)
            results.append({"course_id": course_id, "task_id": r.id})

        logger.info(f"[Embedding] 全量重建已触发，共 {len(results)} 个课程任务")
        return {
            "status": "dispatched",
            "total_courses": len(results),
            "tasks": results,
        }
    except Exception as e:
        logger.error(f"[Embedding] 全量重建失败: {e}")
        raise self.retry(exc=e)
