# TASK-006 提示词模板管理模块

## 任务状态

已完成。

## 任务目标

完成提示词模板管理模块，为任务类型、提示词模板、提示词版本提供基础后端接口，并写入提示词模板相关 `operation_logs`。

本阶段只实现提示词模板管理，不实现 AI 调用、审核中心、成果库、前端页面或统计看板。

## 前置条件

- Stage-01 数据库脚本已通过静态审查；
- Stage-02 FastAPI 后端基础框架已通过；
- Stage-03 用户登录与权限基础模块已通过；
- Stage-04 项目空间管理模块已通过；
- Stage-05 任务与版本管理模块已通过 Fix 复审。

## 允许实现

1. 任务类型列表接口；
2. 提示词模板列表接口；
3. 创建提示词模板接口；
4. 提示词模板详情接口；
5. 更新提示词模板接口；
6. 软删除提示词模板接口；
7. 创建提示词版本接口；
8. 提示词版本列表接口；
9. 启用提示词版本接口；
10. 提示词模板相关 `operation_logs` 写入。

## 建议接口

请以 `docs/02_接口契约与页面清单.md` 为准。如文档已有明确路径，必须优先遵守文档。

建议至少实现：

- `GET /api/task-types`
- `GET /api/prompt-templates`
- `POST /api/prompt-templates`
- `GET /api/prompt-templates/{template_id}`
- `PUT /api/prompt-templates/{template_id}`
- `DELETE /api/prompt-templates/{template_id}`
- `POST /api/prompt-templates/{template_id}/versions`
- `GET /api/prompt-templates/{template_id}/versions`
- `POST /api/prompt-templates/{template_id}/versions/{prompt_version_id}/activate`

## 允许修改文件

- `backend/app/routers/prompts.py`
- `backend/app/services/prompt_service.py`
- `backend/app/repositories/prompt_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-006-prompt-template.md`

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. AI 调用；
2. 审核中心；
3. 成果库；
4. 前端页面；
5. 统计看板。

## 数据库与 Schema 要求

1. 必须严格遵守 `docs/01_数据库Schema冻结说明.md`；
2. 不得新增表；
3. 不得修改字段名；
4. 不得新增未定义状态值；
5. 不得绕过软删除设计；
6. 不得使用 ORM 替代核心 SQL；
7. SQL 必须参数化，不得拼接用户输入；
8. 写操作涉及多表变更或日志写入时，必须使用事务。

涉及表：

- `task_types`
- `prompt_templates`
- `prompt_versions`
- `operation_logs`

## 权限要求

1. 所有接口必须从 `Authorization: Bearer token` 解析当前用户；
2. 任务类型列表可允许已登录用户查看；
3. 提示词模板列表和详情可允许已登录用户查看；
4. 创建、更新、软删除提示词模板建议限制为 admin；
5. 创建提示词版本、启用提示词版本建议限制为 admin；
6. 不得返回 API Key 或任何敏感配置。

## 功能要求

### 任务类型列表

1. 默认过滤 `task_types.is_deleted = 0`；
2. 默认只返回可用或未删除任务类型；
3. 支持基础分页或简单列表；
4. 不得修改任务类型数据。

### 提示词模板列表

1. 默认过滤 `prompt_templates.is_deleted = 0`；
2. 支持 `task_type_id`、`keyword`、`is_active` 等基础筛选；
3. 返回模板基础信息、任务类型信息、当前版本 ID；
4. 不返回不存在字段。

### 创建提示词模板

1. 必须校验 `task_type_id` 存在且未删除；
2. 写入 `prompt_templates`；
3. 可同时创建首个 `prompt_versions`，如实现必须使用同一事务；
4. 必须写入 `operation_logs`；
5. 写操作和日志必须同事务。

### 更新与软删除提示词模板

1. 更新只允许更新 `template_name`、`task_type_id`、`description`、`is_active` 等 Schema 已有字段；
2. 不得修改 `template_id`；
3. UPDATE 必须检查 affected_rows；
4. 删除必须为软删除，设置 `is_deleted`、`deleted_at`、`deleted_by`；
5. 更新和软删除必须写入 `operation_logs`；
6. 写操作和日志必须同事务。

### 提示词版本

1. 创建版本必须关联合法 `template_id`；
2. `version_no` 必须自动生成且避免重复；
3. 必须写入 `prompt_versions.prompt_content`；
4. `change_note` 如请求提供，不得丢弃；
5. 版本列表默认过滤 `prompt_versions.is_deleted = 0`；
6. 启用版本必须校验版本属于当前模板；
7. 启用版本应更新 `prompt_templates.current_version_id`；
8. 创建版本和启用版本必须写入 `operation_logs`；
9. 涉及多表写入时必须使用事务。

## 统一返回格式

成功格式必须保持：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误格式必须类似：

```json
{
  "code": 4001,
  "message": "权限不足",
  "data": null
}
```

不得新增不一致的返回格式。

## 交付要求

完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-006-prompt-template.md`

handoff 必须说明：

1. 实现了哪些接口；
2. 修改了哪些文件；
3. 是否修改了允许范围之外的文件；
4. 权限控制如何实现；
5. 提示词模板相关写操作是否写入 `operation_logs`；
6. 是否使用事务；
7. 是否执行语法检查；
8. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/prompts.py app/services/prompt_service.py app/repositories/prompt_repo.py run.py
```

如当前环境可运行服务，可补充接口级测试；如无法连接 Windows MySQL，不作为本阶段静态审查阻塞，但代码本身不得存在明显运行错误。
