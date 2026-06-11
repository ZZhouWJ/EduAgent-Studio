"""
资源生成异步任务

- 大文本资源生成（长讲义、PPT大纲）
- 批量题库生成
- 资源审核通知
"""
import time
import logging
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def generate_large_resource(self, resource_id: int, resource_type: str, params: dict) -> dict:
    """
    生成长文本学习资源（异步执行）。
    适用于 PPT大纲、复习计划等需要较长生成时间的资源。
    """
    logger.info(f"[Resource] 开始生成资源 {resource_id}，类型={resource_type}")
    try:
        # 模拟：实际应调用 LLM Gateway
        time.sleep(3)
        content = f"# 生成的{resource_type}内容\n\n（由异步任务生成，内容由 LLM 生成）"
        logger.info(f"[Resource] 资源 {resource_id} 生成完成")
        return {
            "status": "success",
            "resource_id": resource_id,
            "content_length": len(content),
            "content_preview": content[:100]
        }
    except Exception as e:
        logger.error(f"[Resource] 生成失败: {e}")
        raise self.retry(exc=e)


@celery_app.task
def batch_generate_quizzes(kp_ids: list[int], difficulty: str, count: int = 10) -> dict:
    """
    批量生成习题。
    kp_ids: 知识点ID列表
    difficulty: 难度等级
    count: 生成题目的数量
    """
    logger.info(f"[Quiz] 批量生成 {count} 道习题，知识点={kp_ids}，难度={difficulty}")
    try:
        # 模拟：实际应调用 LLM
        time.sleep(2)
        quizzes = [f"题目{i}: 示例习题" for i in range(count)]
        return {
            "status": "success",
            "count": len(quizzes),
            "quizzes": quizzes
        }
    except Exception as e:
        logger.error(f"[Quiz] 批量生成失败: {e}")
        raise


@celery_app.task
def notify_resource_ready(resource_id: int, notify_users: list[int]) -> dict:
    """
    资源生成完成后，通知相关用户。
    """
    logger.info(f"[Notify] 资源 {resource_id} 生成完成，通知用户 {notify_users}")
    # 模拟发送通知
    return {"status": "success", "notified_count": len(notify_users)}
