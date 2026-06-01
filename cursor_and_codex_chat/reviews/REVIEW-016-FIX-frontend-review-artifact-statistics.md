# REVIEW-016-FIX 前端审核中心、成果库与统计看板复审报告

## 1. 审查结论

**通过。**

Cursor 已修复 `REVIEW-016-frontend-review-artifact-statistics.md` 中的 4 个阻塞问题：

1. `/artifacts` 已指向真实成果库列表页；
2. 成果库列表 / 详情字段已按后端返回适配；
3. 统计看板已按 Stage-11 后端真实字段和数组返回形态修复；
4. `adopt_separately` 已补齐至少选择一个 output 的前端校验。

允许进入 Stage-17。

## 2. /artifacts 路由是否已指向真实成果库列表页

**已修复。**

`frontend/src/router/index.ts` 中：

- `/artifacts` 已从 `@/pages/artifacts/index.vue` 改为 `@/pages/artifacts/ArtifactList.vue`；
- `/artifacts/:adoptedId` 仍指向 `@/pages/artifacts/ArtifactDetail.vue`；
- 左侧菜单“成果库”通过该路由进入真实成果列表；
- 未发现破坏 `/reviews`、`/statistics`、`/projects`、`/tasks` 等既有路由。

## 3. 成果库列表 / 详情字段是否已适配后端返回

**已修复。**

`frontend/src/common/apis/artifacts/type.ts` 已拆分列表与详情类型：

- `AdoptedOutputListItem` 对齐后端 `_artifact_row_to_dict()`；
- `AdoptedOutputDetail` 对齐后端 `_artifact_detail_to_dict()`。

`ArtifactList.vue` 已改为：

- 采用人读取 `adopted_by_name`；
- 采用时间读取 `adopted_at`；
- 不再依赖错误的 `created_at` 展示采用时间；
- 未发现 Mock 成果数据或敏感字段展示。

`ArtifactDetail.vue` 已改为：

- 正文读取 `output_content`；
- 采用时间读取 `adopted_at`；
- 采用人读取 `adopted_by_real_name || adopted_by_username`；
- 不展示 `password_hash`、API Key 或密钥字段。

说明：当前详情页没有额外兜底 `adopted_by_name / adopter_name / real_name / adopted_by`，但后端详情真实返回 `adopted_by_real_name` 与 `adopted_by_username`，可满足当前接口契约，不作为阻塞。

## 4. 统计看板字段读取是否已修复

**已修复。**

`frontend/src/common/apis/statistics/index.ts` 已将以下接口类型改为数组返回：

- `GET /api/statistics/projects`
- `GET /api/statistics/model-calls`
- `GET /api/statistics/member-contributions`
- `GET /api/statistics/recent-activities`

`StatisticsDashboard.vue` 已新增 `asArray()`，不再固定读取 `res.data.items`。当前已兼容后端真实数组返回，也兼容 `items` 形态。`list / records` 兜底未实现，但 Stage-11 后端真实返回为数组，本轮不阻塞。

字段适配情况：

- overview 已读取 `project_count`、`active_project_count`、`task_count`、`pending_review_count`、`invocation_count`、`success_invocation_count`、`artifact_count`、`total_cost`；
- costs 已读取 `total_cost`、`input_cost`、`output_cost`、`total_tokens`、`cost_by_model`；
- reviews 已读取 `review_count`、`approved_count`、`rejected_count`、`revision_required_count`、各项平均分和 `top_issue_tags`；
- member-contributions 已读取 `user_id`、`real_name`、`task_created_count`、`output_created_count`、`review_count`、`artifact_adopted_count`；
- recent-activities 已读取 `log_id`、`user_id`、`real_name`、`action_type`、`action_desc`、`created_at`。

未发现写死虚假成本、Mock 统计数据或敏感字段展示。

## 5. adopt_separately 至少一个 output 校验是否已补齐

**已修复。**

`frontend/src/pages/tasks/TaskDetail.vue` 中：

- `adopt_source` 仍要求 `source_output_id`；
- `adopt_target` 仍要求 `target_output_id`；
- `manual_merge` 仍要求 `merged_output_title` 和 `merged_content`；
- `adopt_separately` 新增源输出和目标输出选择控件；
- `adopt_separately` 在 `source_output_id` 与 `target_output_id` 都为空时提示“分别保留时至少需要选择一个输出版本”，并阻止调用 merge 接口；
- `merge_strategy` 仍限制为 `adopt_source / adopt_target / manual_merge / adopt_separately`。

## 6. 是否发现新问题

未发现新的阻塞问题。

非阻塞建议：

1. `StatisticsDashboard.vue` 的 `asArray()` 当前兼容数组和 `items`，如后续后端统一为 `list / records`，可再补充兜底。
2. `ArtifactDetail.vue` 可进一步增加 `adopted_by_name`、`real_name`、`adopted_by` 等显示兜底，但当前后端详情字段已满足显示要求。

## 7. 是否发现越界实现

未发现 Stage-16 Fix 新增后端接口、数据库结构修改或新的大模型调用能力。

说明：远程工作区存在大量历史未提交文件变更，包含 backend、database、docs 等目录。本轮根据 handoff 与实际修复点判断，Stage-16 Fix 主要修改集中在前端文件，未发现本轮越界实现。

## 8. 启动或静态检查

尝试检查 Node 环境：

```bash
cd frontend
node -v
```

远程环境返回：

```text
node: command not found
```

因此无法执行 `npm install` 或 `npm run build`。本轮已改为静态审查，重点检查了路由导入、API 路径、页面字段、表单枚举和分支合并校验逻辑，未发现明显语法或路径错误。

## 9. 是否允许进入 Stage-17

**允许进入 Stage-17。**

已发布：

`cursor_and_codex_chat/tasks/todo/TASK-017-final-polish-run-report.md`
