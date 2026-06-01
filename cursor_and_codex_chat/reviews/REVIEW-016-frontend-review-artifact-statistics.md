# REVIEW-016 前端审核中心、成果库与统计看板审查报告

## 1. 审查结论

**不通过，需要继续修改。**

Stage-16 已新增审核中心、成果库、统计看板相关 API 与页面文件，但当前仍存在 4 类阻塞问题：

1. 成果库主路由 `/artifacts` 仍指向占位页，真实 `ArtifactList.vue` 未挂载到菜单入口。
2. 成果库列表 / 详情页面与后端真实返回字段不一致，采用人、采用时间、成果正文会显示为空。
3. 统计看板前端字段和返回结构与后端 Stage-11 接口不匹配，多块统计会显示 0 或空表。
4. 分支合并 `adopt_separately` 策略缺少输出选择和至少一个 output 的前端校验。

因此不允许进入 Stage-17。

## 2. Stage-16 是否遵守任务范围

基本遵守。根据 `HANDOFF-016-frontend-review-artifact-statistics.md` 与本轮审查对象，Stage-16 主要修改集中在 `frontend/*`，未发现本阶段声明新增后端接口、数据库结构或新的大模型调用能力。

说明：远程工作区存在大量历史未提交修改，包含 backend、database、docs 等文件，无法仅凭 `git status` 判断这些文件是否由 Stage-16 新增改动。本报告仅基于 Stage-16 handoff 与本轮要求的前端代码进行归因。

## 3. 审核中心 API 和页面是否正确

**基本正确。**

- `frontend/src/common/apis/reviews/index.ts` 已封装：
  - `GET /api/reviews/pending`
  - `GET /api/reviews/{request_id}`
  - `POST /api/reviews/{request_id}/complete`
  - `GET /api/issue-tags`
- `/reviews` 当前指向 `frontend/src/pages/reviews/index.vue`，该页面已实现待审核列表，不再是占位页。
- 审核列表展示项目、任务、输出、提交人、审核人、状态、提交时间，并支持进入详情。
- 未发现使用 Mock 审核数据或调用不存在接口。

## 4. 完成审核弹窗是否正确

**基本正确。**

`frontend/src/pages/reviews/ReviewDetail.vue` 中完成审核弹窗：

- `review_status` 只提供 `approved`、`rejected`、`revision_required`。
- 评分字段使用 `el-input-number` 并限制 `0-10`。
- `issue_tag_ids` 来自 `GET /api/issue-tags`。
- 提交调用 `POST /api/reviews/{request_id}/complete`。
- 提交成功后刷新审核详情。

未发现百分制评分、非法状态或成果采用越界逻辑。

## 5. issue_tags 选择是否正确

**正确。**

审核详情页在打开完成审核弹窗时调用 `getIssueTagsApi()`，并通过多选方式提交 `issue_tag_ids`。未发现硬编码标签或 Mock 标签作为真实数据。

## 6. 成果库 API 和页面是否正确

**不完全正确，有阻塞问题。**

API 封装路径基本正确：

- `POST /api/outputs/{output_id}/adopt`
- `GET /api/projects/{project_id}/artifacts`
- `GET /api/artifacts/{adopted_id}`
- `POST /api/tasks/{task_id}/branches/merge`

但页面存在两个关键问题：

1. `frontend/src/router/index.ts` 中 `/artifacts` 仍指向 `@/pages/artifacts/index.vue`，而该文件仍是“成果库页面将在下一阶段实现”的占位页。真实实现 `ArtifactList.vue` 没有挂到菜单路由。
2. `ArtifactList.vue` 与后端成果列表字段不一致。后端列表通过 `artifact_service._artifact_row_to_dict()` 返回 `adopted_by_name` 与 `adopted_at`，但前端列表读取 `adopted_by_real_name / adopted_by_username` 和 `created_at`，会导致采用人、采用时间显示为空。

## 7. 采用成果入口是否正确

**部分正确。**

`TaskDetail.vue` 在输出详情中仅当 `outputDetail.status === 'approved'` 时显示“采用为成果”按钮，表单包含 `artifact_title`、`artifact_type`、`release_version`、`adopt_note`，并调用 `adoptOutputApi()`。

需要修复的问题：

- 采用成功后的成果列表 / 详情字段仍需按后端返回修正，否则跳转或查看成果时数据展示不完整。

## 8. 分支合并入口是否正确

**不通过。**

`TaskDetail.vue` 已提供分支合并弹窗，并限制 `merge_strategy` 为：

- `adopt_source`
- `adopt_target`
- `manual_merge`
- `adopt_separately`

其中 `adopt_source` 要求 `source_output_id`，`adopt_target` 要求 `target_output_id`，`manual_merge` 要求标题和内容。

阻塞问题：

- `adopt_separately` 策略没有任何输出选择 UI。
- `handleMerge()` 没有校验 `adopt_separately` 至少选择一个 output。
- 当前可在 `source_output_id` 和 `target_output_id` 都为空时提交 `adopt_separately`，不满足 Stage-16 验收要求。

## 9. 统计看板是否正确

**不通过。**

统计 API 路径已封装，但前端数据结构与后端真实返回不一致：

1. `GET /api/statistics/projects`、`model-calls`、`member-contributions`、`recent-activities` 后端返回数组，前端却读取 `res.data.items`，导致表格为空。
2. 概览字段不匹配。后端返回 `project_count`、`active_project_count`、`task_count`、`pending_review_count`、`invocation_count`、`success_invocation_count`、`failed_invocation_count`、`artifact_count`、`total_tokens`、`total_cost`；前端读取 `total_projects`、`active_projects`、`total_tasks`、`completed_tasks`、`total_outputs`、`approved_outputs`、`total_invocations` 等。
3. 成本字段不匹配。后端返回 `input_cost`、`output_cost`、`total_tokens`、`cost_by_model`、`cost_by_project`、`cost_by_user`；前端读取 `total_input_cost`、`total_output_cost` 等。
4. 审核统计字段不匹配。后端返回 `review_count` 与 `top_issue_tags`，前端读取 `total_reviews`，且未展示 `top_issue_tags`。
5. 成员贡献字段不匹配。后端返回 `task_created_count`、`task_assigned_count`、`output_created_count`、`review_count`、`artifact_adopted_count`、`invocation_count`；前端读取 `output_count`、`approved_output_count`、`total_cost` 等不存在字段。

这些问题会造成统计看板即使后端有真实数据，也显示为 0 或空状态。

## 10. 路由与菜单是否正确

**部分正确。**

- `/reviews`、`/reviews/:requestId` 可用。
- `/statistics` 指向 `StatisticsDashboard.vue`。
- `/artifacts/:adoptedId` 指向 `ArtifactDetail.vue`。

阻塞问题：

- `/artifacts` 指向 `frontend/src/pages/artifacts/index.vue` 占位页，没有指向 `ArtifactList.vue` 或在 `index.vue` 中承载成果列表。

## 11. 是否破坏前面已通过功能

未发现明显破坏 Stage-14 / Stage-15 已通过功能的证据：

- 项目、任务、输出、AI 生成、编辑、批注相关 API 文件仍存在。
- `TaskDetail.vue` 中输出详情、编辑、另存、批注入口仍保留。
- 未发现调用 `/api/auth/register`。

但本轮未能执行前端构建验证，见第 14 节。

## 12. 是否发现真实密钥泄露

未在本轮审查的 Stage-16 前端文件、handoff、API 封装和页面中发现真实数据库密码、真实 API Key、真实 JWT Secret、完整 `sk-` 密钥或真实 token。

## 13. 是否发现越界实现

未发现 Stage-16 新增后端接口、数据库结构修改或新增大模型调用能力。

发现的采用成果与分支合并入口属于 Stage-16 允许范围。

## 14. 启动或静态检查结果

尝试执行 Node 检查：

```bash
cd frontend
node -v
```

结果：当前远程环境提示 `node: command not found`，因此无法执行 `npm install` 或 `npm run build`。

本轮改为静态审查。上述阻塞问题均来自源码与后端契约对照，不依赖构建环境。

## 15. 是否允许进入 Stage-17

**不允许。**

## 16. 必须修复的问题

1. 修复成果库主路由：让 `/artifacts` 打开真实成果列表页面，可选择将路由指向 `ArtifactList.vue`，或将 `artifacts/index.vue` 改为真实列表实现。
2. 修复成果列表字段：列表应读取后端返回的 `adopted_by_name` 和 `adopted_at`，不要只读取 `adopted_by_real_name` / `created_at`。
3. 修复成果详情字段：详情正文应读取后端返回的 `output_content`，采用时间应读取 `adopted_at`；类型定义需同步补充 `adopted_by_name`、`adopted_at`、`output_content`、`adopt_note` 等真实字段。
4. 修复统计看板数据结构：对后端返回数组的接口不要读取 `res.data.items`；可使用 `Array.isArray(res.data) ? res.data : res.data.items || []` 做兼容。
5. 修复统计看板字段名：按后端真实字段重写 overview、costs、reviews、member-contributions 的展示字段。
6. 修复 `adopt_separately` 分支合并策略：提供 source / target output 选择，且至少选择一个 output；校验失败不得调用 `POST /api/tasks/{task_id}/branches/merge`。
7. 修复后重新进行前端构建或至少静态检查，确认路由、导入路径和类型无明显错误。
