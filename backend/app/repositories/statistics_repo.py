"""
统计看板 Repository 层。

所有数据库操作使用参数化 SQL，不拼接用户输入。
不返回 password_hash、API Key、encrypted_api_key、key_iv、key_tag 等敏感字段。
查询默认过滤 is_deleted = 0。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.database import get_db_cursor

# =============================================================================
# 首页概览统计
# =============================================================================

def get_overview_stats(
    is_admin: bool,
    user_id: int,
) -> Dict[str, Any]:
    """
    首页统计概览。

    admin: 全局统计
    非 admin: 只统计用户参与项目的范围内数据

    Returns:
        dict 包含 project_count, active_project_count, task_count,
        pending_review_count, invocation_count, success_invocation_count,
        failed_invocation_count, artifact_count, total_tokens, total_cost
    """
    project_filter, params = _build_project_filter(is_admin, user_id)

    # 项目数量
    project_sql = f"""
        SELECT COUNT(*) AS project_count,
               SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_project_count
        FROM projects
        WHERE is_deleted = 0
        {project_filter}
    """
    with get_db_cursor() as cursor:
        cursor.execute(project_sql, params)
        p = cursor.fetchone()

    # 任务数量
    task_sql = f"""
        SELECT COUNT(*) AS task_count
        FROM project_tasks t
        WHERE t.is_deleted = 0
          AND EXISTS (
              SELECT 1 FROM projects p
              WHERE p.project_id = t.project_id
                AND p.is_deleted = 0
                {project_filter.replace('projects.project_id', 'p.project_id').replace('projects.owner_id', 'p.owner_id')}
          )
    """
    with get_db_cursor() as cursor:
        cursor.execute(task_sql, params)
        t = cursor.fetchone()

    # 待审核数量（review_requests.request_status = 'pending'）
    pending_sql = f"""
        SELECT COUNT(*) AS pending_review_count
        FROM review_requests rr
        WHERE rr.is_deleted = 0
          AND rr.request_status = 'pending'
          {project_filter.replace('projects.project_id', 'rr.project_id')}
    """
    with get_db_cursor() as cursor:
        cursor.execute(pending_sql, params)
        pr = cursor.fetchone()

    # 模型调用统计
    invocation_sql = f"""
        SELECT COUNT(*) AS invocation_count,
               SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success_invocation_count,
               SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_invocation_count,
               COALESCE(SUM(input_tokens), 0) + COALESCE(SUM(output_tokens), 0) AS total_tokens
        FROM ai_invocations ai
        WHERE EXISTS (
            SELECT 1 FROM projects p
            WHERE p.project_id = ai.project_id
              AND p.is_deleted = 0
              {project_filter.replace('projects.project_id', 'p.project_id')}
        )
    """
    with get_db_cursor() as cursor:
        cursor.execute(invocation_sql, params)
        inv = cursor.fetchone()

    # 成果数量
    artifact_sql = f"""
        SELECT COUNT(*) AS artifact_count
        FROM adopted_outputs ao
        WHERE ao.is_deleted = 0
          {project_filter.replace('projects.project_id', 'ao.project_id')}
    """
    with get_db_cursor() as cursor:
        cursor.execute(artifact_sql, params)
        ar = cursor.fetchone()

    # 成本总额
    cost_sql = f"""
        SELECT COALESCE(SUM(cr.total_cost), 0) AS total_cost
        FROM cost_records cr
        WHERE EXISTS (
            SELECT 1 FROM projects p
            WHERE p.project_id = cr.project_id
              AND p.is_deleted = 0
              {project_filter.replace('projects.project_id', 'p.project_id')}
        )
    """
    with get_db_cursor() as cursor:
        cursor.execute(cost_sql, params)
        c = cursor.fetchone()

    return {
        "project_count": p["project_count"] or 0,
        "active_project_count": p["active_project_count"] or 0,
        "task_count": t["task_count"] or 0,
        "pending_review_count": pr["pending_review_count"] or 0,
        "invocation_count": inv["invocation_count"] or 0,
        "success_invocation_count": inv["success_invocation_count"] or 0,
        "failed_invocation_count": inv["failed_invocation_count"] or 0,
        "artifact_count": ar["artifact_count"] or 0,
        "total_tokens": int(inv["total_tokens"] or 0),
        "total_cost": float(c["total_cost"] or 0),
    }


def _build_project_filter(is_admin: bool, user_id: int) -> Tuple[str, List]:
    """
    构建项目过滤条件。

    admin: 无过滤条件
    非 admin: 只允许查看自己参与的项目
    """
    if is_admin:
        return "", []
    return " AND project_id IN (SELECT project_id FROM project_members WHERE user_id = %s AND is_deleted = 0)", [user_id]


# =============================================================================
# 项目统计
# =============================================================================

def list_project_stats(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    项目维度统计列表。

    优先使用 v_project_task_statistics 视图，通过 LEFT JOIN 子查询补齐
    approved_output_count、invocation_count、total_cost。
    """
    params: List = []
    admin_filter = ""
    project_filter = ""

    if not is_admin:
        admin_filter = " AND v.project_id IN (SELECT project_id FROM project_members WHERE user_id = %s AND is_deleted = 0)"
        params.append(user_id)

    if project_id is not None:
        project_filter = " AND v.project_id = %s"
        params.append(project_id)

    sql = f"""
        SELECT
            v.project_id,
            v.project_name,
            v.total_members AS member_count,
            v.total_tasks AS task_count,
            v.total_outputs AS output_count,

            COALESCE(approved.cnt, 0) AS approved_output_count,
            v.total_adopted AS artifact_count,

            COALESCE(invocations_cnt.cnt, 0) AS invocation_count,
            COALESCE(costs.total, 0) AS total_cost

        FROM v_project_task_statistics v

        LEFT JOIN (
            SELECT t.project_id, COUNT(DISTINCT o.output_id) AS cnt
            FROM task_outputs o
            INNER JOIN project_tasks t ON o.task_id = t.task_id AND t.is_deleted = 0
            WHERE o.is_deleted = 0 AND o.status = 'approved'
            GROUP BY t.project_id
        ) approved ON v.project_id = approved.project_id

        LEFT JOIN (
            SELECT project_id, COUNT(*) AS cnt
            FROM ai_invocations
            GROUP BY project_id
        ) invocations_cnt ON v.project_id = invocations_cnt.project_id

        LEFT JOIN (
            SELECT project_id, COALESCE(SUM(total_cost), 0) AS total
            FROM cost_records
            GROUP BY project_id
        ) costs ON v.project_id = costs.project_id

        WHERE 1=1
        {admin_filter}
        {project_filter}
        ORDER BY v.project_created_at DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, params)
        return [_normalize_row(r) for r in cursor.fetchall()]


def get_project_stats_by_id(
    project_id: int,
) -> Optional[Dict[str, Any]]:
    """
    单个项目详细统计。

    字段与 list_project_stats() 完全对齐：
    project_id, project_name, member_count, task_count, output_count,
    approved_output_count, artifact_count, invocation_count, total_cost
    """
    params = [project_id]
    sql = """
        SELECT
            p.project_id,
            p.project_name,

            COALESCE(members.cnt, 0) AS member_count,
            COALESCE(tasks.cnt, 0) AS task_count,
            COALESCE(outputs.cnt, 0) AS output_count,
            COALESCE(approved.cnt, 0) AS approved_output_count,
            COALESCE(artifacts.cnt, 0) AS artifact_count,
            COALESCE(invocations.cnt, 0) AS invocation_count,
            COALESCE(costs.total, 0) AS total_cost

        FROM projects p

        LEFT JOIN (
            SELECT project_id, COUNT(*) AS cnt
            FROM project_members
            WHERE is_deleted = 0
            GROUP BY project_id
        ) members ON p.project_id = members.project_id

        LEFT JOIN (
            SELECT project_id, COUNT(*) AS cnt
            FROM project_tasks
            WHERE is_deleted = 0
            GROUP BY project_id
        ) tasks ON p.project_id = tasks.project_id

        LEFT JOIN (
            SELECT t.project_id, COUNT(DISTINCT o.output_id) AS cnt
            FROM task_outputs o
            INNER JOIN project_tasks t ON o.task_id = t.task_id AND t.is_deleted = 0
            WHERE o.is_deleted = 0
            GROUP BY t.project_id
        ) outputs ON p.project_id = outputs.project_id

        LEFT JOIN (
            SELECT t.project_id, COUNT(DISTINCT o.output_id) AS cnt
            FROM task_outputs o
            INNER JOIN project_tasks t ON o.task_id = t.task_id AND t.is_deleted = 0
            WHERE o.is_deleted = 0 AND o.status = 'approved'
            GROUP BY t.project_id
        ) approved ON p.project_id = approved.project_id

        LEFT JOIN (
            SELECT project_id, COUNT(*) AS cnt
            FROM adopted_outputs
            WHERE is_deleted = 0
            GROUP BY project_id
        ) artifacts ON p.project_id = artifacts.project_id

        LEFT JOIN (
            SELECT project_id, COUNT(*) AS cnt
            FROM ai_invocations
            GROUP BY project_id
        ) invocations ON p.project_id = invocations.project_id

        LEFT JOIN (
            SELECT project_id, COALESCE(SUM(total_cost), 0) AS total
            FROM cost_records
            GROUP BY project_id
        ) costs ON p.project_id = costs.project_id

        WHERE p.project_id = %s AND p.is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return _normalize_row(row) if row else None


# =============================================================================
# 模型调用统计
# =============================================================================

def get_model_call_stats(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    模型调用统计。

    权限过滤由 service 层根据 project_id 决定 project_ids 范围后传入。
    SQL 从 ai_invocations 出发，JOIN ai_models 获取模型信息，
    JOIN projects 过滤已删除项目，确保不跨项目统计。

    参数顺序（与 SQL 占位符严格对应）：
      [1] ai.project_id = %s  或  ai.project_id IN (...%)
      [2] ai.created_at >= %s
      [3] ai.created_at <= %s
    """
    params: List = []

    # 1. project 过滤
    project_filter = ""
    if project_id is not None:
        # 有明确 project_id：严格限制 ai.project_id = %s
        project_filter = "ai.project_id = %s"
        params.append(project_id)
    elif not is_admin:
        # 非 admin 无 project_id：限制在参与项目范围内
        member_sql = """
            SELECT DISTINCT project_id FROM project_members
            WHERE user_id = %s AND is_deleted = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(member_sql, (user_id,))
            rows = cursor.fetchall()
        project_ids = [r["project_id"] for r in rows]
        if not project_ids:
            return []
        ids_ph = ",".join(["%s"] * len(project_ids))
        project_filter = f"ai.project_id IN ({ids_ph})"
        params.extend(project_ids)
    # admin 无 project_id：无 project 过滤条件

    # 2. date 过滤（列表累积，避免 date_from 被 date_to 覆盖）
    date_conditions = []
    if date_from:
        date_conditions.append("ai.created_at >= %s")
        params.append(date_from)
    if date_to:
        date_conditions.append("ai.created_at <= %s")
        params.append(date_to + " 23:59:59")

    # 构建 WHERE 子句
    conditions = ["m.is_deleted = 0", project_filter]
    conditions.extend(date_conditions)
    where_clause = " AND ".join(c for c in conditions if c)

    sql = f"""
        SELECT
            m.model_id,
            m.model_name,
            m.display_name,
            mp.provider_name,
            COUNT(ai.invocation_id) AS call_count,
            COUNT(ai.invocation_id) AS total_invocations,
            SUM(CASE WHEN ai.status = 'success' THEN 1 ELSE 0 END) AS success_count,
            SUM(CASE WHEN ai.status = 'failed' THEN 1 ELSE 0 END) AS failed_count,
            SUM(CASE WHEN ai.status = 'timeout' THEN 1 ELSE 0 END) AS timeout_count,
            SUM(CASE WHEN ai.status = 'blocked' THEN 1 ELSE 0 END) AS blocked_count,
            COALESCE(SUM(ai.input_tokens),  0) AS total_input_tokens,
            COALESCE(SUM(ai.output_tokens), 0) AS total_output_tokens,
            COALESCE(SUM(ai.input_tokens) + SUM(ai.output_tokens), 0) AS total_tokens,
            COALESCE(AVG(ai.latency_ms), 0) AS avg_latency_ms,
            CASE
                WHEN COUNT(ai.invocation_id) > 0
                THEN ROUND(
                    SUM(CASE WHEN ai.status = 'success' THEN 1 ELSE 0 END) * 100.0
                    / COUNT(ai.invocation_id), 2)
                ELSE 0.00
            END AS success_rate
        FROM ai_invocations ai
        INNER JOIN ai_models m
            ON ai.model_id = m.model_id
        LEFT JOIN model_providers mp
            ON m.provider_id = mp.provider_id AND mp.is_deleted = 0
        WHERE {where_clause}
        GROUP BY m.model_id, m.model_name, m.display_name, mp.provider_name
        ORDER BY call_count DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, params)
        return [_normalize_row(r) for r in cursor.fetchall()]


# =============================================================================
# 成本统计
# =============================================================================

def get_cost_stats(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Dict[str, Any]:
    """
    成本统计。
    """
    params: List = []
    project_filter = ""
    date_filter = ""

    if project_id is not None:
        project_filter = " AND cr.project_id = %s"
        params.append(project_id)

    if date_from:
        date_filter += " AND cr.created_at >= %s"
        params.append(date_from)

    if date_to:
        date_filter += " AND cr.created_at <= %s"
        params.append(date_to + " 23:59:59")

    member_filter = ""
    if not is_admin:
        member_filter = " AND cr.project_id IN (SELECT project_id FROM project_members WHERE user_id = %s AND is_deleted = 0)"
        params.append(user_id)

    # 总体成本
    total_sql = f"""
        SELECT
            COALESCE(SUM(cr.total_cost), 0) AS total_cost,
            COALESCE(SUM(cr.input_cost), 0) AS input_cost,
            COALESCE(SUM(cr.output_cost), 0) AS output_cost,
            COALESCE(SUM(cr.total_tokens), 0) AS total_tokens
        FROM cost_records cr
        WHERE 1=1
        {project_filter}
        {date_filter}
        {member_filter}
    """
    with get_db_cursor() as cursor:
        cursor.execute(total_sql, params)
        total = cursor.fetchone()

    # 按模型分成本
    by_model_params = params.copy()
    by_model_filter = project_filter
    by_model_date = date_filter
    by_model_member = member_filter
    if project_id is not None:
        by_model_filter = " AND cr.project_id = %s"
    by_model_sql = f"""
        SELECT
            cr.model_id,
            m.model_name,
            m.display_name,
            COALESCE(mp.provider_name, '') AS provider_name,
            COUNT(*) AS call_count,
            COALESCE(SUM(cr.input_cost), 0) AS input_cost,
            COALESCE(SUM(cr.output_cost), 0) AS output_cost,
            COALESCE(SUM(cr.total_cost), 0) AS total_cost,
            COALESCE(SUM(cr.total_tokens), 0) AS total_tokens,
            COALESCE(SUM(cr.input_tokens), 0) AS input_tokens,
            COALESCE(SUM(cr.output_tokens), 0) AS output_tokens
        FROM cost_records cr
        INNER JOIN ai_models m ON cr.model_id = m.model_id AND m.is_deleted = 0
        LEFT JOIN model_providers mp ON m.provider_id = mp.provider_id AND mp.is_deleted = 0
        WHERE 1=1
        {by_model_filter}
        {by_model_date}
        {by_model_member}
        GROUP BY cr.model_id, m.model_name, m.display_name, mp.provider_name
        ORDER BY total_cost DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(by_model_sql, by_model_params)
        cost_by_model = [_normalize_row(r) for r in cursor.fetchall()]

    # 按项目分成本
    by_project_params = params.copy()
    by_project_member = member_filter
    by_project_sql = f"""
        SELECT
            cr.project_id,
            p.project_name,
            COUNT(*) AS call_count,
            COALESCE(SUM(cr.total_tokens), 0) AS total_tokens,
            COALESCE(SUM(cr.total_cost), 0) AS total_cost
        FROM cost_records cr
        INNER JOIN projects p ON cr.project_id = p.project_id AND p.is_deleted = 0
        WHERE 1=1
        {project_filter}
        {date_filter}
        {by_project_member}
        GROUP BY cr.project_id, p.project_name
        ORDER BY total_cost DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(by_project_sql, by_project_params)
        rows = cursor.fetchall()
        cost_by_project = [
            {**_normalize_row(r), "input_tokens": 0, "output_tokens": 0, "avg_cost_per_call": (r.get("total_cost") or 0) / (r.get("call_count") or 1)}
            for r in rows
        ]

    # 按用户分成本
    by_user_params = params.copy()
    by_user_sql = f"""
        SELECT
            cr.user_id,
            u.real_name,
            COALESCE(SUM(cr.total_cost), 0) AS total_cost,
            COALESCE(SUM(cr.total_tokens), 0) AS total_tokens
        FROM cost_records cr
        INNER JOIN users u ON cr.user_id = u.user_id AND u.is_deleted = 0
        WHERE 1=1
        {project_filter}
        {date_filter}
        {member_filter}
        GROUP BY cr.user_id, u.real_name
        ORDER BY total_cost DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(by_user_sql, by_user_params)
        cost_by_user = [_normalize_row(r) for r in cursor.fetchall()]

    return {
        "total_cost": float(total["total_cost"] or 0),
        "input_cost": float(total["input_cost"] or 0),
        "output_cost": float(total["output_cost"] or 0),
        "total_tokens": int(total["total_tokens"] or 0),
        "currency": "CNY",
        "cost_by_model": cost_by_model,
        "cost_by_project": cost_by_project,
        "cost_by_user": cost_by_user,
    }


# =============================================================================
# 审核质量统计
# =============================================================================

def get_review_stats(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    审核质量统计。
    """
    params: List = []
    project_filter = ""
    member_filter = ""

    if project_id is not None:
        project_filter = " AND rr.project_id = %s"
        params.append(project_id)

    if not is_admin:
        member_filter = " AND rr.project_id IN (SELECT project_id FROM project_members WHERE user_id = %s AND is_deleted = 0)"
        params.append(user_id)

    # 审核数量统计
    review_sql = f"""
        SELECT
            COUNT(DISTINCT rr.request_id) AS review_count,
            SUM(CASE WHEN rr.request_status = 'approved' THEN 1 ELSE 0 END) AS approved_count,
            SUM(CASE WHEN rr.request_status = 'rejected' THEN 1 ELSE 0 END) AS rejected_count,
            SUM(CASE WHEN rr.request_status = 'revision_required' THEN 1 ELSE 0 END) AS revision_required_count
        FROM review_requests rr
        WHERE rr.is_deleted = 0
        {project_filter}
        {member_filter}
    """
    with get_db_cursor() as cursor:
        cursor.execute(review_sql, params)
        counts = cursor.fetchone()

    # 平均评分
    score_sql = f"""
        SELECT
            COALESCE(AVG(orr.accuracy_score), 0) AS avg_accuracy_score,
            COALESCE(AVG(orr.completeness_score), 0) AS avg_completeness_score,
            COALESCE(AVG(orr.logic_score), 0) AS avg_logic_score,
            COALESCE(AVG(orr.format_score), 0) AS avg_format_score,
            COALESCE(AVG(orr.usability_score), 0) AS avg_usability_score,
            COALESCE(AVG(orr.risk_score), 0) AS avg_risk_score
        FROM output_reviews orr
        INNER JOIN review_requests rr
            ON orr.request_id = rr.request_id AND rr.is_deleted = 0
        WHERE orr.is_deleted = 0
        {project_filter.replace('rr.project_id', 'rr.project_id')}
        {member_filter}
    """
    with get_db_cursor() as cursor:
        cursor.execute(score_sql, params)
        scores = cursor.fetchone()

    # Top 问题标签
    tag_params = params.copy()
    tag_sql = f"""
        SELECT
            it.tag_name,
            it.tag_code,
            it.severity,
            COUNT(DISTINCT oir.relation_id) AS tag_count
        FROM output_issue_relations oir
        INNER JOIN output_reviews orr
            ON oir.review_id = orr.review_id AND orr.is_deleted = 0
        INNER JOIN review_requests rr
            ON orr.request_id = rr.request_id AND rr.is_deleted = 0
        INNER JOIN issue_tags it
            ON oir.tag_id = it.tag_id AND it.is_deleted = 0
        WHERE oir.is_deleted = 0
        {project_filter}
        {member_filter}
        GROUP BY it.tag_name, it.tag_code, it.severity
        ORDER BY tag_count DESC
        LIMIT 10
    """
    with get_db_cursor() as cursor:
        cursor.execute(tag_sql, tag_params)
        top_tags = [_normalize_row(r) for r in cursor.fetchall()]

    return {
        "review_count": counts["review_count"] or 0,
        "approved_count": counts["approved_count"] or 0,
        "rejected_count": counts["rejected_count"] or 0,
        "revision_required_count": counts["revision_required_count"] or 0,
        "avg_accuracy_score": round(float(scores["avg_accuracy_score"] or 0), 2),
        "avg_completeness_score": round(float(scores["avg_completeness_score"] or 0), 2),
        "avg_logic_score": round(float(scores["avg_logic_score"] or 0), 2),
        "avg_format_score": round(float(scores["avg_format_score"] or 0), 2),
        "avg_usability_score": round(float(scores["avg_usability_score"] or 0), 2),
        "avg_risk_score": round(float(scores["avg_risk_score"] or 0), 2),
        "top_issue_tags": top_tags,
    }


# =============================================================================
# 成员贡献统计
# =============================================================================

def get_member_contribution_stats(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    成员贡献统计。

    权限规则：
    - admin: 全局（不限 project_id）
    - 非 admin + project_id 指定：当前用户参与该项目 -> 返回该项目所有成员贡献
    - 非 admin + project_id 未指定：返回当前用户参与的所有项目中的所有成员贡献
    """
    params: List = []
    project_scope_filter = ""

    if project_id is not None:
        # 指定了 project_id：只统计该项目
        project_scope_filter = " AND pm.project_id = %s"
        params.append(project_id)
    elif not is_admin:
        # 非 admin 未指定 project_id：限制在参与项目的范围内
        project_scope_filter = " AND pm.project_id IN (SELECT project_id FROM project_members WHERE user_id = %s AND is_deleted = 0)"
        params.append(user_id)

    sql = f"""
        SELECT
            pm.user_id,
            u.real_name,
            COUNT(DISTINCT pm.project_id) AS project_count,
            COALESCE(SUM(
                (SELECT COUNT(*) FROM project_tasks pt
                 WHERE pt.project_id = pm.project_id
                   AND pt.created_by = pm.user_id
                   AND pt.is_deleted = 0)
            ), 0) AS task_created_count,
            COALESCE(SUM(
                (SELECT COUNT(*) FROM project_tasks pt2
                 WHERE pt2.project_id = pm.project_id
                   AND pt2.assignee_id = pm.user_id
                   AND pt2.is_deleted = 0)
            ), 0) AS task_assigned_count,
            COALESCE(SUM(
                (SELECT COUNT(*) FROM task_outputs o
                 INNER JOIN project_tasks pt ON o.task_id = pt.task_id AND pt.is_deleted = 0
                 WHERE pt.project_id = pm.project_id
                   AND o.created_by = pm.user_id
                   AND o.is_deleted = 0)
            ), 0) AS output_created_count,
            COALESCE(SUM(
                (SELECT COUNT(*) FROM review_requests rr
                 WHERE rr.project_id = pm.project_id
                   AND rr.reviewer_id = pm.user_id
                   AND rr.is_deleted = 0)
            ), 0) AS review_count,
            COALESCE(SUM(
                (SELECT COUNT(*) FROM adopted_outputs ao
                 WHERE ao.project_id = pm.project_id
                   AND ao.adopted_by = pm.user_id
                   AND ao.is_deleted = 0)
            ), 0) AS artifact_adopted_count,
            COALESCE(SUM(
                (SELECT COUNT(*) FROM ai_invocations ai
                 WHERE ai.project_id = pm.project_id
                   AND ai.created_by = pm.user_id)
            ), 0) AS invocation_count
        FROM project_members pm
        INNER JOIN users u ON pm.user_id = u.user_id AND u.is_deleted = 0
        WHERE pm.is_deleted = 0
        {project_scope_filter}
        GROUP BY pm.user_id, u.real_name
        ORDER BY project_count DESC, task_created_count DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, params)
        return [_normalize_row(r) for r in cursor.fetchall()]


# =============================================================================
# 最近操作动态
# =============================================================================

def get_recent_activities(
    is_admin: bool,
    user_id: int,
    project_id: Optional[int] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    最近操作动态。
    """
    params: List = []
    project_filter = ""
    member_filter = ""

    if project_id is not None:
        project_filter = " AND ol.project_id = %s"
        params.append(project_id)

    if not is_admin:
        member_filter = " AND ol.project_id IN (SELECT project_id FROM project_members WHERE user_id = %s AND is_deleted = 0)"
        params.append(user_id)

    safe_limit = min(max(1, limit), 100)

    sql = f"""
        SELECT
            ol.log_id,
            ol.user_id,
            u.real_name,
            ol.action_type,
            ol.target_type,
            ol.target_id,
            ol.action_desc,
            ol.created_at
        FROM operation_logs ol
        INNER JOIN users u ON ol.user_id = u.user_id AND u.is_deleted = 0
        WHERE 1=1
        {project_filter}
        {member_filter}
        ORDER BY ol.created_at DESC
        LIMIT %s
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, params + [safe_limit])
        return [_normalize_row(r) for r in cursor.fetchall()]


# =============================================================================
# 权限辅助
# =============================================================================

def check_user_can_access_project(project_id: int, user_id: int, is_admin: bool) -> bool:
    """判断用户是否可以访问某项目。"""
    if is_admin:
        return True
    sql = """
        SELECT 1 FROM project_members
        WHERE project_id = %s AND user_id = %s AND is_deleted = 0
    """
    with get_db_cursor() as cursor:
        cursor.execute(sql, (project_id, user_id))
        return cursor.fetchone() is not None


# =============================================================================
# 工具
# =============================================================================

def _normalize_row(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """清理行数据中的 None，转数值类型为合理默认值。"""
    if row is None:
        return None
    result = {}
    for key, value in row.items():
        if value is None:
            result[key] = 0
        elif isinstance(value, (int, float)):
            result[key] = value
        else:
            result[key] = value
    return result
