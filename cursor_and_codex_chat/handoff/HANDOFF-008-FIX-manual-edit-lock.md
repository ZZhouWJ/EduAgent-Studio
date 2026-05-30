# HANDOFF-008-FIX：Stage-08 人工编辑、批注与乐观锁模块修复版

## 任务状态

**完成** — Stage-08 Fix 修复问题均已处理。

---

## 一、Codex 未通过原因

| # | 问题 | 严重程度 |
|---|---|---|
| 1 | 验收要求接口路径为 `POST /api/outputs/{output_id}/save-as-new-version`，但只实现了 `/save-as` | 阻塞 |
| 2 | `comment_type` 未按 Schema 枚举校验（应只允许 `comment`、`suggestion`、`approval`）| 阻塞 |
| 3 | 批注状态更新权限未正确识别项目内 leader（只用全局 `project_leader` 角色字符串）| 阻塞 |

---

## 二、本次修复的问题列表

1. 新增 `POST /api/outputs/{output_id}/save-as-new-version` 路由，两个路径共用同一 service 函数
2. `comment_type` 增加 Schema 枚举校验（`VALID_COMMENT_TYPE = {"comment", "suggestion", "approval"}`）
3. 批注状态更新权限改用 `project_repo.is_user_project_leader/teacher/reviewer(project_id, user_id)` 判断项目内角色
4. `update_comment_status` 增加 `updated_by` 字段写入
5. 新增 `task_repo.get_comment_project_context(comment_id)` 获取批注关联的 project_id
6. 新增 `project_repo.is_user_project_teacher(project_id, user_id)`
7. 新增 `project_repo.is_user_project_reviewer(project_id, user_id)`

---

## 三、本次修改文件

| 文件 | 修改内容 |
| --- | --- |
| `backend/app/repositories/task_repo.py` | 顶部增加 `VALID_COMMENT_TYPE`；删除 Stage-08 追加的重复 `VALID_COMMENT_STATUS`；`update_comment_status` 增加 `updated_by` 参数；新增 `get_comment_project_context(comment_id)` |
| `backend/app/repositories/project_repo.py` | 新增 `is_user_project_teacher(project_id, user_id)`；新增 `is_user_project_reviewer(project_id, user_id)` |
| `backend/app/services/task_service.py` | `create_output_comment` 增加 `comment_type` 枚举校验；`update_comment_status` 权限判断改用项目内角色函数；事务内传入 `updated_by` |
| `backend/app/routers/tasks.py` | `/save-as` 路由改名为 `save_output_as`；新增 `/save-as-new-version` 路由；抽取 `_save_as_impl()` 统一调用 service |

**说明**：未修改 `database/*`、`frontend/*`、`docs/*`。

---

## 四、是否补齐 POST /api/outputs/{output_id}/save-as-new-version

**是**。新增了验收指定路径：

```
POST /api/outputs/{output_id}/save-as          # 保留兼容路径
POST /api/outputs/{output_id}/save-as-new-version  # 验收指定路径
```

---

## 五、/save-as-new-version 是否复用原有另存逻辑

**是**。两个路由均通过 `_save_as_impl()` 内部函数调用同一个 `task_service.save_output_as_new_version()`，无逻辑分叉。

```python
@router.post("/api/outputs/{output_id}/save-as")
async def save_output_as(...):      # 兼容路径
    return _save_as_impl(...)

@router.post("/api/outputs/{output_id}/save-as-new-version")
async def save_output_as_new_version(...):  # 验收路径
    return _save_as_impl(...)

def _save_as_impl(...):             # 共用实现
    return task_service.save_output_as_new_version(...)
```

---

## 六、comment_type 允许值是否限制为 comment / suggestion / approval

**是**。

```python
VALID_COMMENT_TYPE = {"comment", "suggestion", "approval"}   # task_repo.py

# task_service.py create_output_comment()
if comment_type.strip() not in task_repo.VALID_COMMENT_TYPE:
    raise ValidationException(
        message=f"无效的批注类型: {comment_type}，允许值: {', '.join(task_repo.VALID_COMMENT_TYPE)}"
    )
```

---

## 七、非法 comment_type 如何返回错误

非法 `comment_type`（如 `修改建议`、`事实问题`）返回统一 `ValidationException`：

```json
{
  "code": 4000,
  "message": "无效的批注类型: 修改建议，允许值: comment, suggestion, approval",
  "data": null
}
```

不将非法值交给数据库层报错。

---

## 八、批注状态更新如何识别项目内 leader

**修复前**（错误）：

```python
elif "project_leader" in user.get("roles", []):   # 全局角色字符串
```

**修复后**（正确）：

```python
# 1. 通过 get_comment_project_context 获取 comment 所属 project_id
ctx = task_repo.get_comment_project_context(comment_id)
project_id = ctx["project_id"]

# 2. 用项目内角色函数判断
if _is_admin(user):
    pass
elif commenter_id == user_id:                              # 批注创建人
    pass
elif project_repo.is_user_project_leader(project_id, user_id):    # 项目内 leader
    pass
elif project_repo.is_user_project_teacher(project_id, user_id):   # 项目内 teacher
    pass
elif project_repo.is_user_project_reviewer(project_id, user_id):   # 项目内 reviewer
    pass
else:
    raise ForbiddenException(message="无权更新此批注状态")
```

新增的 repository 函数：

```python
# project_repo.py
def is_user_project_teacher(project_id, user_id):
    SELECT 1 FROM project_members
    WHERE project_id=%s AND user_id=%s
      AND project_role='teacher' AND is_deleted=0

def is_user_project_reviewer(project_id, user_id):
    SELECT 1 FROM project_members
    WHERE project_id=%s AND user_id=%s
      AND project_role='reviewer' AND is_deleted=0
```

---

## 九、是否仍错误依赖全局 project_leader

**否**。已完全移除全局 `"project_leader"` 字符串检查，改为通过 `project_id` 调用 `project_repo.is_user_project_leader(project_id, user_id)`。

---

## 十、是否修改 database

**否**。

---

## 十一、是否修改 frontend

**否**。

---

## 十二、是否实现审核中心

**否**。

---

## 十三、是否实现成果库

**否**。

---

## 十四、Python 语法检查命令

```bash
cd backend
python -m py_compile app/repositories/task_repo.py app/repositories/project_repo.py app/services/task_service.py app/routers/tasks.py
```

结果：`EXIT:0`（全部通过）。

---

## 十五、当前环境限制

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查
2. 本次未修改 `database/` 目录，未修改表结构

---

## 十六、需要 Codex 复审的重点

1. **接口路径**：`POST /api/outputs/{output_id}/save-as-new-version` 是否可访问，两个路由是否共用同一 service 逻辑
2. **comment_type 枚举**：非法值是否在 service 层被拒绝，不进入数据库
3. **批注状态权限**：`is_user_project_leader/teacher/reviewer` 是否正确使用 `project_members.project_role` 而非全局角色
4. **无越界**：确认未实现审核中心、成果库、前端页面
5. **updated_by 字段**：`update_comment_status` 是否传入 `updated_by`
6. **语法检查**：所有修改文件是否通过 `py_compile`

---

## 十七、验收清单

- [x] 新增 `POST /api/outputs/{output_id}/save-as-new-version`
- [x] 两个路由共用同一 service 函数
- [x] `VALID_COMMENT_TYPE = {"comment", "suggestion", "approval"}`
- [x] 非法 `comment_type` 在 service 层抛出 `ValidationException`
- [x] 移除全局 `"project_leader"` 字符串检查
- [x] 使用 `project_repo.is_user_project_leader(project_id, user_id)`
- [x] 新增 `is_user_project_teacher` 和 `is_user_project_reviewer`
- [x] `update_comment_status` 传入 `updated_by`
- [x] 新增 `get_comment_project_context(comment_id)` 获取 project_id
- [x] 所有 Python 语法检查通过
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`

---

**本修复完成后停止，等待 Codex 复审。**
