"""
Embedding 异步任务

- 批量计算知识点 embedding
- 增量更新资源 embedding
- 定期重新计算全部 embedding
"""
import time
import logging
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def compute_knowledge_point_embeddings(self, course_id: int) -> dict:
    """
    批量计算课程知识点的 embedding 向量。
    存储到 pgvector 表 knowledge_point_embeddings。
    """
    logger.info(f"[Embedding] 开始计算课程 {course_id} 的知识点 embedding")
    try:
        # 模拟：实际应从数据库读取知识点，然后调用 embedding 服务
        kp_ids = [1, 2, 3, 5, 8, 12]
        results = []
        for kp_id in kp_ids:
            # 模拟 embedding 计算
            time.sleep(0.2)
            embedding = [0.1] * 768  # 768维 mock embedding
            results.append({
                "kp_id": kp_id,
                "embedding_dim": 768,
                "status": "success"
            })
        logger.info(f"[Embedding] 课程 {course_id} 完成，共处理 {len(results)} 个知识点")
        return {
            "status": "success",
            "course_id": course_id,
            "processed_count": len(results)
        }
    except Exception as e:
        logger.error(f"[Embedding] 计算失败: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True)
def compute_resource_embedding(self, resource_id: int) -> dict:
    """
    为单个学习资源计算 embedding。
    """
    logger.info(f"[Embedding] 计算资源 {resource_id} 的 embedding")
    try:
        # 模拟
        time.sleep(0.5)
        return {
            "status": "success",
            "resource_id": resource_id,
            "chunk_count": 3
        }
    except Exception as e:
        logger.error(f"[Embedding] 资源 {resource_id} 计算失败: {e}")
        raise
