"""
提示词模板 Service 层。

处理任务类型、提示词模板、提示词版本相关业务逻辑。
复用 user_repo / project_repo 中的权限判断工具。
"""

import re
from typing import Any, Dict, List, Optional

from app.database import get_db_transaction
from app.repositories import prompt_repo, user_repo
from app.utils.exceptions import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


PROMPT_VARIABLE_PATTERN = re.compile(
    r"\{\{\s*([A-Za-z_][A-Za-z0-9_.-]{0,63})\s*\}\}"
)
MAX_PREVIEW_VARIABLES = 100
MAX_PREVIEW_VALUE_LENGTH = 50_000
MAX_PREVIEW_TOTAL_LENGTH = 200_000


# =============================================================================
# 权限辅助函数
# =============================================================================

def _require_auth(token: str) -> Dict[str, Any]:
    """解析 Token，获取当前用户。"""
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        raise UnauthorizedException(message="未登录或登录已过期，请重新登录")
    return user


def _is_admin(user: Dict[str, Any]) -> bool:
    return "admin" in user.get("roles", [])


def _is_teacher(user: Dict[str, Any]) -> bool:
    return "teacher" in user.get("roles", [])


def _is_project_leader(user: Dict[str, Any]) -> bool:
    return "project_leader" in user.get("roles", [])


def _can_manage_template(template_created_by: Optional[int], user: Dict[str, Any]) -> bool:
    """判断用户是否有权管理模板：admin / teacher / project_leader / 模板创建人。"""
    if _is_admin(user):
        return True
    if _is_teacher(user):
        return True
    if _is_project_leader(user):
        return True
    if template_created_by is not None and user["user_id"] == template_created_by:
        return True
    return False


def _check_template_write_permission(
    template_id: int,
    user: Dict[str, Any],
) -> None:
    """检查用户是否有权修改模板，失败则抛出异常。"""
    if _can_manage_template(
        prompt_repo.get_template_created_by(template_id),
        user,
    ):
        return
    raise ForbiddenException(message="无权管理此模板")


# =============================================================================
# 任务类型列表
# =============================================================================

def list_task_types(
    token: str,
    status_only_active: bool = True,
) -> List[Dict[str, Any]]:
    """查询任务类型列表（已登录用户均可查看）。"""
    _require_auth(token)

    rows = prompt_repo.list_task_types(status_only_active=status_only_active)
    return [_task_type_row_to_dict(r) for r in rows]


# =============================================================================
# 提示词模板列表
# =============================================================================

def list_templates(
    token: str,
    task_type_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """分页查询提示词模板列表（已登录用户均可查看）。"""
    _require_auth(token)

    rows, total = prompt_repo.list_templates(
        task_type_id=task_type_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    return {
        "items": [_template_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# =============================================================================
# 创建提示词模板（事务：INSERT template + INSERT operation_logs）
# =============================================================================

def create_template(
    token: str,
    template_name: str,
    task_type_id: int,
    description: Optional[str] = None,
    initial_prompt_content: Optional[str] = None,
    change_note: Optional[str] = None,
    activate: bool = False,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """创建提示词模板（admin / teacher / project_leader 可操作）。"""
    user = _require_auth(token)

    if not _is_admin(user) and not _is_teacher(user) and not _is_project_leader(user):
        raise ForbiddenException(message="无权创建模板")

    if not template_name or not template_name.strip():
        raise ValidationException(message="模板名称不能为空")

    normalized_prompt = (
        initial_prompt_content.strip() if initial_prompt_content else None
    )
    if activate and not normalized_prompt:
        raise ValidationException(message="启用模板前必须提供初始提示词")

    task_type = prompt_repo.get_task_type_by_id(task_type_id)
    if task_type is None:
        raise NotFoundException(message="任务类型不存在")

    template_id: int = 0

    with get_db_transaction() as conn:
        template_id = prompt_repo.create_template(
            template_name=template_name.strip(),
            task_type_id=task_type_id,
            description=(description.strip() if description else None),
            created_by=user["user_id"],
            is_active=activate,
            conn=conn,
        )

        if normalized_prompt:
            version_id = prompt_repo.create_version(
                template_id=template_id,
                version_no="1",
                prompt_content=normalized_prompt,
                change_note=(change_note.strip() if change_note else "初始版本"),
                created_by=user["user_id"],
                conn=conn,
            )
            prompt_repo.set_current_version(
                template_id=template_id,
                version_id=version_id,
                conn=conn,
            )

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="prompt_template:create",
            action_desc=(
                f"创建提示词模板及初始版本: {template_name.strip()}"
                if normalized_prompt
                else f"创建提示词模板草稿: {template_name.strip()}"
            ),
            target_type="prompt_template",
            target_id=template_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    template = prompt_repo.get_template_by_id(template_id)
    return _template_detail_to_dict(template)


# =============================================================================
# 提示词模板详情
# =============================================================================

def get_template_detail(
    token: str,
    template_id: int,
) -> Dict[str, Any]:
    """获取模板详情（已登录用户均可查看）。"""
    _require_auth(token)

    template = prompt_repo.get_template_by_id(template_id)
    if template is None:
        raise NotFoundException(message="模板不存在")

    return _template_detail_to_dict(template)


# =============================================================================
# 更新提示词模板（事务：UPDATE template + INSERT operation_logs）
# =============================================================================

def update_template(
    token: str,
    template_id: int,
    template_name: Optional[str] = None,
    task_type_id: Optional[int] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """更新提示词模板（admin / teacher / project_leader / 模板创建人可操作）。"""
    user = _require_auth(token)

    template = prompt_repo.get_template_by_id(template_id)
    if template is None:
        raise NotFoundException(message="模板不存在")

    _check_template_write_permission(template_id, user)

    if template_name is not None and not template_name.strip():
        raise ValidationException(message="模板名称不能为空")

    if task_type_id is not None:
        task_type = prompt_repo.get_task_type_by_id(task_type_id)
        if task_type is None:
            raise NotFoundException(message="任务类型不存在")

    with get_db_transaction() as conn:
        affected = prompt_repo.update_template(
            template_id=template_id,
            template_name=(template_name.strip() if template_name else None),
            task_type_id=task_type_id,
            description=description,
            is_active=is_active,
            updated_by=user["user_id"],
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="模板不存在或无权更新")

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="prompt_template:update",
            action_desc=f"更新提示词模板: {template_id}",
            target_type="prompt_template",
            target_id=template_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    updated = prompt_repo.get_template_by_id(template_id)
    return _template_detail_to_dict(updated)


# =============================================================================
# 软删除提示词模板（事务：UPDATE template + INSERT operation_logs）
# =============================================================================

def delete_template(
    token: str,
    template_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """软删除提示词模板（admin / teacher / project_leader / 模板创建人可操作）。"""
    user = _require_auth(token)

    template = prompt_repo.get_template_by_id(template_id)
    if template is None:
        raise NotFoundException(message="模板不存在")

    _check_template_write_permission(template_id, user)

    with get_db_transaction() as conn:
        affected = prompt_repo.soft_delete_template(
            template_id=template_id,
            deleted_by=user["user_id"],
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="模板不存在或无权删除")

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="prompt_template:delete",
            action_desc=f"删除提示词模板: {template_id}",
            target_type="prompt_template",
            target_id=template_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()


# =============================================================================
# 提示词版本列表
# =============================================================================

def list_template_versions(
    token: str,
    template_id: int,
) -> List[Dict[str, Any]]:
    """查询模板的版本列表（已登录用户均可查看）。"""
    _require_auth(token)

    template = prompt_repo.get_template_by_id(template_id)
    if template is None:
        raise NotFoundException(message="模板不存在")

    rows = prompt_repo.list_template_versions(template_id)
    return [_version_row_to_dict(r) for r in rows]


# =============================================================================
# 创建提示词版本（事务：INSERT version + INSERT operation_logs）
# =============================================================================

def create_version(
    token: str,
    template_id: int,
    version_no: Optional[str] = None,
    prompt_content: Optional[str] = None,
    change_note: Optional[str] = None,
    auto_activate: bool = False,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    创建提示词版本（admin / teacher / project_leader / 模板创建人可操作）。

    version_no 若不提供则自动生成。
    若 auto_activate=True 且模板无 current_version_id，自动设为当前版本。
    """
    user = _require_auth(token)

    template = prompt_repo.get_template_by_id(template_id)
    if template is None:
        raise NotFoundException(message="模板不存在")

    _check_template_write_permission(template_id, user)

    if not prompt_content or not prompt_content.strip():
        raise ValidationException(message="提示词内容不能为空")

    if version_no is None or not str(version_no).strip():
        version_no = str(prompt_repo.get_next_version_no(template_id))
    else:
        version_no = str(version_no).strip()

    version_id: int = 0

    with get_db_transaction() as conn:
        version_id = prompt_repo.create_version(
            template_id=template_id,
            version_no=version_no,
            prompt_content=prompt_content.strip(),
            change_note=(change_note.strip() if change_note else None),
            created_by=user["user_id"],
            conn=conn,
        )

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="prompt_version:create",
            action_desc=f"创建提示词版本: {version_no}",
            target_type="prompt_version",
            target_id=version_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )

        if auto_activate or template.get("current_version_id") is None:
            prompt_repo.set_current_version(
                template_id=template_id,
                version_id=version_id,
                conn=conn,
            )

        conn.commit()

    version = prompt_repo.get_version_by_id(version_id)
    return _version_detail_to_dict(version)


# =============================================================================
# 启用提示词版本（事务：UPDATE template + INSERT operation_logs）
# =============================================================================

def activate_version(
    token: str,
    template_id: int,
    version_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """启用指定版本为模板当前活动版本（admin / teacher / project_leader / 模板创建人可操作）。"""
    user = _require_auth(token)

    template = prompt_repo.get_template_by_id(template_id)
    if template is None:
        raise NotFoundException(message="模板不存在")

    _check_template_write_permission(template_id, user)

    version = prompt_repo.get_version_by_template_and_id(version_id, template_id)
    if version is None:
        raise NotFoundException(message="版本不存在或不属于此模板")

    with get_db_transaction() as conn:
        affected = prompt_repo.set_current_version(
            template_id=template_id,
            version_id=version_id,
            conn=conn,
        )
        if affected == 0:
            conn.rollback()
            raise NotFoundException(message="模板不存在或无权操作")

        user_repo.insert_operation_log_with_conn(
            user_id=user["user_id"],
            action_type="prompt_version:activate",
            action_desc=f"启用提示词版本: version_id={version_id}",
            target_type="prompt_version",
            target_id=version_id,
            project_id=None,
            task_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            conn=conn,
        )
        conn.commit()

    updated_template = prompt_repo.get_template_by_id(template_id)
    return _template_detail_to_dict(updated_template)


# =============================================================================
# 渲染提示词预览
# =============================================================================

def render_template(
    token: str,
    template_id: int,
    version_id: Optional[int] = None,
    variables: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """安全替换模板占位符并返回预览，不执行表达式或模型调用。"""
    _require_auth(token)

    template = prompt_repo.get_template_by_id(template_id)
    if template is None:
        raise NotFoundException(message="模板不存在")

    selected_version_id = version_id or template.get("current_version_id")
    if selected_version_id is None:
        raise ValidationException(message="模板尚无可渲染版本")

    if version_id is not None:
        owned_version = prompt_repo.get_version_by_template_and_id(
            version_id=version_id,
            template_id=template_id,
        )
        if owned_version is None:
            raise NotFoundException(message="版本不存在或不属于此模板")

    version = prompt_repo.get_version_by_id(selected_version_id)
    if version is None:
        raise NotFoundException(message="提示词版本不存在")

    content = version.get("prompt_content") or ""
    required_variables = list(dict.fromkeys(PROMPT_VARIABLE_PATTERN.findall(content)))
    supplied = variables or {}

    if len(supplied) > MAX_PREVIEW_VARIABLES:
        raise ValidationException(message="预览变量数量不能超过 100 个")

    unknown_variables = sorted(set(supplied) - set(required_variables))
    if unknown_variables:
        names = "、".join(unknown_variables[:5])
        raise ValidationException(message=f"模板未声明以下变量：{names}")

    total_length = 0
    for name, value in supplied.items():
        if not isinstance(value, str):
            raise ValidationException(message=f"变量 {name} 必须是文本")
        if len(value) > MAX_PREVIEW_VALUE_LENGTH:
            raise ValidationException(message=f"变量 {name} 内容过长")
        total_length += len(value)
    if total_length > MAX_PREVIEW_TOTAL_LENGTH:
        raise ValidationException(message="预览变量总内容过长")

    def replace_variable(match: re.Match[str]) -> str:
        name = match.group(1)
        return supplied[name] if name in supplied else match.group(0)

    rendered_content = PROMPT_VARIABLE_PATTERN.sub(replace_variable, content)
    missing_variables = [name for name in required_variables if name not in supplied]

    return {
        "template_id": template_id,
        "version_id": version["prompt_version_id"],
        "version_no": version["version_no"],
        "required_variables": required_variables,
        "missing_variables": missing_variables,
        "rendered_content": rendered_content,
    }


# =============================================================================
# 数据转换辅助函数
# =============================================================================

def _task_type_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {}
    return {
        "task_type_id": row["task_type_id"],
        "type_name": row["type_name"],
        "type_code": row["type_code"],
        "description": row.get("description"),
        "default_template_id": row.get("default_template_id"),
        "status": row["status"],
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _template_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """模板列表行（不含 prompt_content）。"""
    if row is None:
        return {}
    return {
        "template_id": row["template_id"],
        "template_name": row["template_name"],
        "task_type_id": row["task_type_id"],
        "type_name": row.get("type_name"),
        "type_code": row.get("type_code"),
        "description": row.get("description"),
        "current_version_id": row.get("current_version_id"),
        "current_version_no": row.get("current_version_no"),
        "is_active": bool(row.get("is_active")),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "created_by": row.get("created_by"),
        "creator_username": row.get("creator_username"),
        "creator_real_name": row.get("creator_real_name"),
    }


def _template_detail_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """模板详情（含当前版本信息）。"""
    if row is None:
        return {}
    result = _template_row_to_dict(row)
    result["current_version_no"] = row.get("current_version_no")
    result["current_prompt_content"] = row.get("current_prompt_content")
    return result


def _version_row_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """版本列表行。"""
    if row is None:
        return {}
    return {
        "prompt_version_id": row["prompt_version_id"],
        "template_id": row["template_id"],
        "version_no": row["version_no"],
        "prompt_content": row.get("prompt_content"),
        "change_note": row.get("change_note"),
        "is_active": bool(row.get("is_active")),
        "created_at": row.get("created_at"),
        "created_by": row.get("created_by"),
        "creator_username": row.get("creator_username"),
        "creator_real_name": row.get("creator_real_name"),
    }


def _version_detail_to_dict(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return _version_row_to_dict(row)
