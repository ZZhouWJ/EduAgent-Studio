# TASK-009 审核中心模块

## 任务状态

待 Cursor 开发。

## 任务目标

实现审核中心模块，包括输出提交审核、待审核列表、审核详情、完成审核、评分写入、问题标签关联、状态流转与审核相关 `operation_logs`。

本阶段不实现成果库、统计看板或前端页面。

## 前置条件

- Stage-01 数据库脚本已通过静态审查；
- Stage-02 FastAPI 后端基础框架已通过；
- Stage-03 用户登录与权限基础模块已通过；
- Stage-04 项目空间管理模块已通过；
- Stage-05 任务与版本管理模块已通过；
- Stage-06 提示词模板管理模块已通过；
- Stage-07 模型管理、Mock 模型调用、调用日志和成本记录模块已通过 Fix R2 复审；
- Stage-08 人工编辑、批注与乐观锁模块已通过 Fix 复审。

## 允许实现

1. 输出提交审核接口；
2. 待审核列表接口；
3. 审核详情接口；
4. 完成审核接口；
5. 审核评分写入 `output_reviews`；
6. 审核请求状态更新；
7. 输出状态更新；
8. 任务状态更新；
9. 问题标签关联 `output_issue_relations`；
10. 审核相关 `operation_logs` 写入。

## 建议接口

请以 `docs/02_接口契约与页面清单.md` 为准。如文档已有明确路径，必须优先遵守文档。

建议至少实现：

- `POST /api/outputs/{output_id}/submit-review`
- `GET /api/reviews/pending`
- `GET /api/reviews/{request_id}`
- `POST /api/reviews/{request_id}/complete`

## 允许修改文件

- `backend/app/routers/reviews.py`
- `backend/app/services/review_service.py`
- `backend/app/repositories/review_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-009-review-center.md`

如确实需要复用任务或输出权限判断，可少量修改：

- `backend/app/services/task_service.py`
- `backend/app/repositories/task_repo.py`

但必须在 handoff 中说明理由。

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 成果库；
2. 统计看板；
3. 前端页面。

## 数据库与 Schema 要求

必须严格遵守已冻结 Schema，不得新增表、改字段或新增状态值。

重点涉及表：

- `review_requests`
- `output_reviews`
- `issue_tags`
- `output_issue_relations`
- `task_outputs`
- `project_tasks`
- `operation_logs`
- 可读取：`projects`、`project_members`、`users`

## 权限要求

1. 所有接口必须从 `Authorization: Bearer token` 解析当前用户；
2. 非项目成员不得提交、查看或完成审核；
3. admin 可查看和处理全部审核；
4. 项目内 leader、teacher、reviewer 可查看待审核和完成审核；
5. 普通 member 可提交审核，但不得完成审核；
6. reviewer_id 如指定，必须是项目内成员或有审核权限的用户；
7. 不得泄露其他项目的审核请求、输出内容或评分。

## 输出提交审核要求

`POST /api/outputs/{output_id}/submit-review` 必须：

1. 校验输出版本存在且 `is_deleted = 0`；
2. 校验当前用户有权限访问输出所属项目；
3. 校验输出未处于不可提交状态；
4. 插入 `review_requests`；
5. `request_status` 默认 `pending`；
6. `submitter_id` 为当前用户；
7. 如传入 `reviewer_id`，校验审核人合法；
8. 更新 `task_outputs.status = 'submitted'`；
9. 视业务需要更新 `project_tasks.status = 'submitted'`；
10. 写入 `operation_logs`；
11. 审核请求、输出状态、任务状态、日志必须在同一事务内。

## 待审核列表要求

`GET /api/reviews/pending` 必须：

1. admin 可查看全部 pending；
2. 项目内 teacher、leader、reviewer 可查看自己有权限项目的 pending；
3. 普通 member 不得查看他人待审核列表；
4. 支持 page、page_size；
5. 支持 project_id、task_id、reviewer_id 等基础过滤；
6. 默认过滤 `review_requests.is_deleted = 0`；
7. 返回分页结构；
8. 不返回 `password_hash` 或敏感信息。

## 审核详情要求

`GET /api/reviews/{request_id}` 必须：

1. 校验审核请求存在且未删除；
2. 校验当前用户有权限访问该审核请求所属项目；
3. 返回审核请求基础信息；
4. 返回输出版本基础信息和 content；
5. 返回提交人、审核人基本信息；
6. 可返回历史评分或问题标签；
7. 不泄露无关项目数据。

## 完成审核要求

`POST /api/reviews/{request_id}/complete` 必须：

1. 校验审核请求存在且未删除；
2. 校验 `request_status = 'pending'`；
3. 校验当前用户有完成审核权限；
4. 校验 `review_status` 只能为 `approved`、`rejected`、`revision_required`；
5. 写入 `output_reviews`；
6. 更新 `review_requests.request_status`；
7. 更新 `review_requests.reviewed_at`；
8. 更新 `task_outputs.status`；
9. 更新 `project_tasks.status`；
10. 如传入 `issue_tag_ids`，校验每个 `issue_tags` 存在且未删除；
11. 写入 `output_issue_relations`；
12. 写入 `operation_logs`；
13. 所有写操作必须在同一事务内；
14. `affected_rows` 必须检查，不得失败后返回 success。

## 状态流转要求

必须使用 Schema 冻结文档允许的状态值：

- `review_requests.request_status`: `pending` / `approved` / `rejected` / `revision_required`
- `task_outputs.status`: `submitted` / `approved` / `rejected` / `revision_required` 等已定义值
- `project_tasks.status`: `submitted` / `approved` / `rejected` / `revision_required` 等已定义值

不得新增自定义状态。

## Repository 与事务要求

1. 审核相关 SQL 集中在 `review_repo.py`；
2. service 层不得直接写 SQL；
3. SQL 必须全部使用参数化查询；
4. 不得拼接用户输入到 SQL；
5. 不得使用 ORM；
6. 查询默认过滤 `is_deleted = 0`；
7. 多表写入必须使用事务；
8. repository 方法不得随意 `commit`；
9. service 层统一 `commit` / `rollback`；
10. `affected_rows` 必须被检查；
11. 连接和 cursor 必须正确关闭。

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

- `cursor_and_codex_chat/handoff/HANDOFF-009-review-center.md`

handoff 必须说明：

1. 实现了哪些接口；
2. 修改了哪些文件；
3. 是否修改了允许范围之外的文件；
4. 审核提交如何写入 `review_requests`；
5. 完成审核如何写入 `output_reviews` 和 `output_issue_relations`；
6. 输出状态和任务状态如何更新；
7. 是否写入 `operation_logs`；
8. 是否使用事务；
9. 是否执行语法检查；
10. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/reviews.py app/services/review_service.py app/repositories/review_repo.py run.py
```

如修改了 `task_service.py` 或 `task_repo.py`，也请执行：

```bash
python3 -m py_compile app/services/task_service.py app/repositories/task_repo.py
```

如当前环境可运行服务，可补充接口级测试；如无法连接 Windows MySQL，不作为本阶段静态审查阻塞，但代码本身不得存在明显运行错误。

