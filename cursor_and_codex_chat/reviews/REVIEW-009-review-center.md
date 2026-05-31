# REVIEW-009 审核中心模块审查报告

## 1. 审查结论

**不通过。**

Stage-09 已实现审核中心主要接口和三层结构，Python 语法检查通过，未发现成果库、统计看板、前端页面或 Stage-10 越界实现。但本轮发现多个阻塞问题，集中在审核权限、状态流转和事务结果校验。

因此：**不允许进入 Stage-10**，本次不发布 `TASK-010-artifact-library.md`。

## 2. Stage-09 是否遵守任务范围

结论：**基本遵守范围。**

- 已实现审核中心相关路由、service 和 repository；
- 未发现成果库、统计看板、前端页面实现；
- 未发现写入 `adopted_outputs`；
- 未发现提前实现 Stage-10 成果采用接口；
- 未发现本阶段修改 `database/`、`frontend/` 或 `docs/01_数据库Schema冻结说明.md`。

说明：工作区中 `database/` 和 `docs/` 存在历史变更，但按文件时间检查，未发现 Stage-09 本轮新增越界修改。

## 3. 输出提交审核接口是否正确

结论：**不通过。**

已实现：

- `POST /api/outputs/{output_id}/submit-review`；
- 校验 output 存在且未删除；
- 校验当前用户有项目访问权限；
- 防止同一 output 重复 pending 提交；
- 插入 `review_requests`；
- 更新 `task_outputs.status = 'submitted'`；
- 更新 `project_tasks.status = 'submitted'`；
- 写入 `operation_logs`；
- 以上写操作位于同一事务内。

阻塞问题：

1. `reviewer_id` 未校验。`backend/app/services/review_service.py:100-108` 直接把请求中的 `reviewer_id` 写入 `review_requests`，没有校验该用户是否存在、是否是项目成员、是否具备审核权限。这可能导致非法 reviewer、跨项目 reviewer，或依赖数据库外键报错。
2. 提交审核时未检查状态更新的 `affected_rows`。`backend/app/services/review_service.py:110-120` 调用了 `update_output_status()` 和 `update_task_status()`，但没有检查返回值，无法发现状态更新失败后仍继续写日志并提交事务的风险。

## 4. 待审核列表是否正确

结论：**不通过。**

已实现：

- `GET /api/reviews/pending`；
- admin 可查看全部；
- 默认查询 `request_status = 'pending'`；
- 默认过滤 `review_requests.is_deleted = 0`；
- 支持 `project_id`、`page`、`page_size`；
- 返回分页结构；
- 列表不返回完整 content 或 password_hash。

阻塞问题：

1. 普通 member 被指定为 reviewer 时看不到分配给自己的请求。`backend/app/repositories/review_repo.py:123-132` 非 admin 只允许项目内 `leader/teacher/reviewer` 查看，缺少 `r.reviewer_id = 当前用户` 的例外。用户要求：`reviewer_id` 指定为当前用户时，普通成员也可以看到分配给自己的审核请求。

## 5. 审核详情是否正确

结论：**需要修改。**

已实现：

- `GET /api/reviews/{request_id}`；
- request_id 必须存在且未删除；
- 返回审核请求、项目、任务、输出版本、完整 output content、submitter/reviewer 基本信息；
- 不返回 password_hash、API Key 或密钥字段。

风险：

- 当前详情权限只校验项目访问权限，普通项目成员可查看本项目任意审核详情和完整输出 content。若按审核中心权限收紧，应与待审列表/完成审核的权限策略保持一致：admin、项目内 leader/teacher/reviewer、指定 reviewer、提交者可查看相关请求；普通无关 member 不应查看他人审核详情。

该问题建议与本轮权限修复一起处理。

## 6. 完成审核接口是否正确

结论：**不通过。**

已实现：

- `POST /api/reviews/{request_id}/complete`；
- 校验 request 存在且未删除；
- 校验当前 `request_status = pending`；
- 写入 `output_reviews`；
- 更新 `review_requests.request_status`；
- 更新 `task_outputs.status`；
- 更新 `project_tasks.status`；
- 写入 `output_issue_relations`；
- 写入 `operation_logs`；
- 返回 `review_id`。

阻塞问题：

1. 完成审核允许非法业务状态 `pending`。`backend/app/repositories/review_repo.py:25` 的 `VALID_REVIEW_STATUS` 包含 `pending`，而 `backend/app/services/review_service.py:247-250` 直接使用该集合校验完成审核入参。用户要求完成审核只允许 `approved`、`rejected`、`revision_required`。
2. 指定 reviewer 时权限过宽。`backend/app/services/review_service.py:301-325` 中，若 `reviewer_id` 不为空，仍允许项目内 reviewer/leader/teacher 完成审核；用户要求指定 reviewer、admin、项目 leader、teacher 可完成，但项目内普通 reviewer 不应越过指定 reviewer。
3. 提交者可以通过指定自己为 reviewer 完成自审。`backend/app/services/review_service.py:278-325` 没有拦截 `submitter_id == 当前用户`，而 `_can_complete_review()` 中指定 reviewer 优先通过。用户要求输出提交者不能审核自己的输出，除非同时是 admin / leader / teacher。
4. 完成审核时未检查多个状态更新的 `affected_rows`。`backend/app/services/review_service.py:293-310` 未检查 `update_review_request_status()`、`update_output_status()`、`update_task_status()` 返回值，可能出现审核记录已插入但状态更新失败仍提交的风险。

## 7. 状态流转是否正确

结论：**不通过。**

`approved`、`rejected`、`revision_required` 三种状态映射逻辑存在，但由于完成审核允许 `pending`，状态流转不满足验收要求。必须为完成审核单独定义允许集合：

- `approved`
- `rejected`
- `revision_required`

不能把 `review_requests` 表的全部枚举值直接用于完成审核入参。

未发现把 `approved` 直接写入 `adopted_outputs`。

## 8. issue_tag_ids 和 output_issue_relations 是否正确

结论：**基本通过。**

- 已实现 `GET /api/issue-tags`；
- 查询 `issue_tags` 并过滤 `is_deleted = 0`；
- 返回 `tag_id`、`tag_name`、`tag_code`、`description`、`severity`；
- 完成审核时批量校验 `issue_tag_ids` 存在且未删除；
- 写入 `output_issue_relations`；
- 与 `output_reviews`、状态更新和日志处于同一事务。

建议：

- `GET /api/issue-tags` 当前无需认证，和本阶段“所有接口从 Authorization 解析当前用户”的总体要求不一致。标签本身不敏感，但建议补齐 token 校验，保持接口风格一致。

## 9. 审核权限是否符合要求

结论：**不通过。**

通过项：

- admin 可审核所有项目；
- 项目内 leader / teacher / reviewer 使用 `project_members.project_role` 判断；
- 非项目成员无法完成审核；
- 不依赖全局角色字符串。

阻塞问题：

- 指定 reviewer 场景未正确收紧；
- 提交者自审未拦截；
- 普通 member 作为指定 reviewer 时待审列表不可见；
- 提交审核阶段未校验 reviewer_id 是否属于项目或具备审核权限。

## 10. operation_logs 是否写入

结论：**基本通过。**

- 提交审核写入 `review:submit`；
- 完成审核写入 `review:complete`；
- 日志写入与业务写操作位于同一事务内。

但由于部分状态更新未检查 `affected_rows`，仍存在状态更新失败而日志提交的风险，需要修复。

## 11. Repository 层和参数化 SQL 是否符合要求

结论：**基本通过。**

- 审核相关 SQL 集中在 `review_repo.py`；
- `review_service.py` 未发现直接写 SQL；
- SQL 使用 `%s` 参数绑定；
- 未发现 ORM；
- 查询默认过滤 `is_deleted = 0`；
- repository 方法未随意 `commit`；
- `create_review_request()` 和 `create_output_review()` 使用 `cursor.lastrowid` 返回 ID。

问题：

- service 层未检查状态更新的 affected_rows，不满足“affected_rows 是否被检查”的要求。

## 12. 事务一致性是否符合要求

结论：**需要继续修改。**

提交审核和完成审核都使用了事务，整体方向正确。但由于没有检查关键 UPDATE 的返回值，无法保证以下情况被正确回滚：

- `review_requests` 插入成功但 `task_outputs` 或 `project_tasks` 状态未更新；
- `output_reviews` 插入成功但 `review_requests`、`task_outputs` 或 `project_tasks` 状态未更新；
- 状态更新失败但 `operation_logs` 写入后仍提交。

## 13. 是否发现越界实现

结论：**未发现。**

- 未发现修改 `database/`；
- 未发现修改 `frontend/`；
- 未发现修改 `docs/01_数据库Schema冻结说明.md`；
- 未发现成果库、统计看板或 Stage-10 内容；
- 未发现写入 `adopted_outputs`；
- 未发现成果采用接口。

## 14. 运行或静态检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/reviews.py app/services/review_service.py app/repositories/review_repo.py run.py
python3 -m py_compile app/services/task_service.py app/repositories/task_repo.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准，不因无法连接 MySQL 阻塞。

## 15. 是否允许进入 Stage-10

**不允许。**

必须先完成 `TASK-009-FIX-review-center.md`。

## 16. 必须修复的问题

1. 提交审核时校验 `reviewer_id`：必须存在，且为当前项目成员或具备审核权限；不得允许跨项目或不存在的 reviewer。
2. 待审核列表允许普通 member 查看分配给自己的审核请求，即 `r.reviewer_id = 当前用户` 的 pending 请求。
3. 完成审核入参 `review_status` 只允许 `approved`、`rejected`、`revision_required`，不得允许 `pending`。
4. 指定 reviewer 场景收紧权限：若 `reviewer_id` 不为空，只有指定 reviewer、admin、项目 leader、teacher 可以完成审核；项目内 reviewer 不能越过指定 reviewer。
5. 拦截提交者自审：提交者不能完成自己的审核请求，除非同时是 admin / 项目 leader / 项目 teacher。
6. 提交审核和完成审核必须检查所有关键状态更新的 `affected_rows`，失败时 rollback 并返回清晰错误。
7. 建议补齐 `GET /api/issue-tags` 的登录校验，保持本阶段接口认证一致性。

