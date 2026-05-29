# TASK-005 任务与版本管理模块

## 任务目标

完成任务与版本管理模块，为项目内任务、任务分支、输出版本提供基础后端接口，并写入相关 `operation_logs`。

本阶段只实现任务与版本管理，不实现 AI 调用、提示词模板、审核中心、成果库或前端页面。

## 前置条件

- Stage-01 数据库脚本已通过静态审查；
- Stage-02 FastAPI 后端基础框架已通过；
- Stage-03 用户登录与权限基础模块已通过；
- Stage-04 项目空间管理模块已通过 Fix R2 复审。

## 允许实现

1. 项目任务列表接口；
2. 创建项目任务接口；
3. 任务详情接口；
4. 更新任务接口；
5. 软删除任务接口；
6. 创建任务分支接口；
7. 任务分支列表接口；
8. 输出版本列表接口；
9. 输出版本详情接口；
10. 输出版本时间线接口；
11. 基础人工输出版本创建接口；
12. 任务、分支、版本相关 `operation_logs` 写入。

## 建议接口

请以 `docs/02_接口契约与页面清单.md` 为准。如文档已有明确路径，必须优先遵守文档。

建议至少实现：

- `GET /api/projects/{project_id}/tasks`
- `POST /api/projects/{project_id}/tasks`
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/branches`
- `GET /api/tasks/{task_id}/branches`
- `GET /api/tasks/{task_id}/outputs`
- `GET /api/outputs/{output_id}`
- `GET /api/outputs/{output_id}/timeline`
- `POST /api/tasks/{task_id}/outputs/manual`

## 允许修改文件

- `backend/app/routers/tasks.py`
- `backend/app/services/task_service.py`
- `backend/app/repositories/task_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-005-task-version-management.md`

如确实需要复用项目权限判断，可少量修改：

- `backend/app/services/project_service.py`
- `backend/app/repositories/project_repo.py`

但必须在 handoff 中说明理由。

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. AI 调用；
2. 提示词模板；
3. 审核中心；
4. 成果库；
5. 前端页面。

## 数据库与 Schema 要求

1. 必须严格遵守 `docs/01_数据库Schema冻结说明.md`；
2. 不得新增表；
3. 不得修改字段名；
4. 不得新增未定义状态值；
5. 不得绕过软删除设计；
6. 不得使用 ORM 替代核心 SQL；
7. SQL 必须参数化，不得拼接用户输入；
8. 写操作涉及多表变更或日志写入时，必须使用事务。

## 权限要求

1. 所有接口必须从 `Authorization: Bearer token` 解析当前用户；
2. admin 可访问全部项目任务；
3. 非 admin 用户只能访问自己参与项目下的任务；
4. 创建、更新、删除任务原则上仅允许 admin、项目 owner 或项目 leader；
5. 查看任务、分支、版本允许项目成员访问；
6. 不得返回 `password_hash` 或任何 API Key。

## 任务管理要求

1. 项目任务列表默认过滤 `project_tasks.is_deleted = 0`；
2. 支持基础分页；
3. 可支持 `keyword`、`status`、`task_type` 等筛选，但不得使用未冻结状态值；
4. 创建任务必须写入 `created_at`、`created_by`；
5. 更新任务只允许更新业务允许字段，不得修改 `task_id`、`project_id` 等主键或归属字段；
6. 删除任务必须为软删除，设置 `is_deleted`、`deleted_at`、`deleted_by`；
7. 创建、更新、软删除任务必须写入 `operation_logs`。

## 分支管理要求

1. 创建任务分支必须关联合法 `task_id` 和 `project_id`；
2. 分支状态值必须遵守 Schema 冻结文档；
3. 分支列表默认过滤 `task_branches.is_deleted = 0`；
4. 创建分支必须写入 `operation_logs`；
5. 不实现分支合并业务，除非接口契约明确要求；如实现，必须只做基础记录，不进入审核或成果库逻辑。

## 输出版本要求

1. 输出版本列表默认过滤 `task_outputs.is_deleted = 0`；
2. 输出版本详情必须包含版本基础信息；
3. 输出版本时间线应基于 `task_outputs` 的父子关系、版本号、创建时间或相关记录组织；
4. 基础人工输出版本创建接口只允许创建 `source_type` 为人工输入或 Schema 已定义的等价值；
5. 不得调用 AI；
6. 不得实现提示词模板；
7. 不得实现审核流程；
8. 不得实现成果库发布。

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

## 事务与日志要求

以下操作必须写入 `operation_logs`，并与核心写操作处于同一事务：

- 创建任务；
- 更新任务；
- 软删除任务；
- 创建任务分支；
- 创建人工输出版本。

如 repository 层提供可选 `conn` 参数，service 层应统一控制 `commit` / `rollback`。

## 交付要求

完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-005-task-version-management.md`

handoff 必须说明：

1. 实现了哪些接口；
2. 修改了哪些文件；
3. 是否修改了允许范围之外的文件；
4. 权限控制如何实现；
5. 任务、分支、版本写操作是否写入 `operation_logs`；
6. 是否使用事务；
7. 是否执行语法检查；
8. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py
```

如当前环境可运行服务，可补充接口级测试；如无法连接 Windows MySQL，不作为本阶段静态审查阻塞，但代码本身不得存在明显运行错误。
