# TASK-016-FIX 前端审核中心、成果库与统计看板修复任务

## 任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-016-frontend-review-artifact-statistics.md` 修复 Stage-16 阻塞问题，使前端审核中心、成果库、统计看板页面与 Stage-09 / Stage-10 / Stage-11 后端真实接口契约一致。

## 允许修改

- `frontend/src/router/index.ts`
- `frontend/src/pages/artifacts/index.vue`
- `frontend/src/pages/artifacts/ArtifactList.vue`
- `frontend/src/pages/artifacts/ArtifactDetail.vue`
- `frontend/src/common/apis/artifacts/index.ts`
- `frontend/src/common/apis/artifacts/type.ts`
- `frontend/src/pages/statistics/StatisticsDashboard.vue`
- `frontend/src/common/apis/statistics/index.ts`
- `frontend/src/common/apis/statistics/type.ts`
- `frontend/src/pages/tasks/TaskDetail.vue`
- `cursor_and_codex_chat/handoff/HANDOFF-016-FIX-frontend-review-artifact-statistics.md`

如确实需要整理相关前端样式或局部组件，可少量修改 `frontend/src` 下相关文件，但必须在 handoff 中说明。

## 禁止修改

- `backend/*`
- `database/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 新后端接口；
2. 数据库结构修改；
3. 新的大模型调用能力；
4. Stage-17 最终打磨任务；
5. 大规模重构前端模板结构。

## 必须修复的问题

### 一、修复成果库主路由

当前 `/artifacts` 仍打开 `frontend/src/pages/artifacts/index.vue` 占位页。

要求：

1. `/artifacts` 必须展示真实成果库列表；
2. 可将路由改为 `ArtifactList.vue`；
3. 或将 `artifacts/index.vue` 改为真实列表页面；
4. 左侧菜单“成果库”点击后不得再出现“成果库页面将在下一阶段实现”。

### 二、修复成果库列表字段

后端成果列表返回字段包括：

- `adopted_id`
- `project_id`
- `task_id`
- `output_id`
- `artifact_title`
- `artifact_type`
- `release_version`
- `adopted_by`
- `adopted_by_name`
- `adopted_at`
- `task_title`
- `output_title`
- `version_no`

要求：

1. 成果列表采用人显示 `adopted_by_name`；
2. 成果列表采用时间显示 `adopted_at`；
3. 不得只读取 `adopted_by_real_name`、`adopted_by_username`、`created_at`；
4. 空数据状态仍保留；
5. 不得使用 Mock 成果数据。

### 三、修复成果详情字段

后端成果详情返回字段包括：

- `adopted_id`
- `project_id`
- `project_name`
- `task_id`
- `task_title`
- `output_id`
- `output_title`
- `version_no`
- `output_content`
- `output_status`
- `artifact_title`
- `artifact_type`
- `release_version`
- `adopted_by`
- `adopted_by_username`
- `adopted_by_real_name`
- `adopted_at`
- `created_at`
- `updated_at`

要求：

1. 成果正文显示 `output_content`；
2. 采用时间优先显示 `adopted_at`；
3. 采用人显示 `adopted_by_real_name || adopted_by_username || adopted_by_name`；
4. 类型定义同步补齐真实字段；
5. 不得展示 password_hash、API Key 或任何密钥字段。

### 四、修复统计看板返回结构适配

后端以下接口返回数组，不是分页对象：

- `GET /api/statistics/projects`
- `GET /api/statistics/model-calls`
- `GET /api/statistics/member-contributions`
- `GET /api/statistics/recent-activities`

要求：

1. 前端不得只读取 `res.data.items`；
2. 必须兼容数组返回；
3. 可使用 `Array.isArray(res.data) ? res.data : res.data.items || []` 做兼容；
4. 无数据时显示空数组或 Empty；
5. 不得写死统计数据。

### 五、修复统计看板字段名

`overview` 应使用后端真实字段：

- `project_count`
- `active_project_count`
- `task_count`
- `pending_review_count`
- `invocation_count`
- `success_invocation_count`
- `failed_invocation_count`
- `artifact_count`
- `total_tokens`
- `total_cost`

`costs` 应使用：

- `total_cost`
- `input_cost`
- `output_cost`
- `total_tokens`
- `cost_by_model`
- `cost_by_project`
- `cost_by_user`
- `currency`

`reviews` 应使用：

- `review_count`
- `approved_count`
- `rejected_count`
- `revision_required_count`
- `avg_accuracy_score`
- `avg_completeness_score`
- `avg_logic_score`
- `avg_format_score`
- `avg_usability_score`
- `avg_risk_score`
- `top_issue_tags`

`member-contributions` 应使用：

- `user_id`
- `real_name`
- `project_count`
- `task_created_count`
- `task_assigned_count`
- `output_created_count`
- `review_count`
- `artifact_adopted_count`
- `invocation_count`

要求：

1. 不再读取不存在的 `total_projects`、`active_projects`、`total_reviews`、`total_input_cost`、`output_count`、`approved_output_count`、`total_cost` 等错误字段；
2. 统计卡片、表格和排行都应能展示真实后端字段；
3. 无数据时展示 0 或 Empty。

### 六、修复 adopt_separately 分支合并校验

当前 `adopt_separately` 可以在 `source_output_id` 和 `target_output_id` 都为空时提交。

要求：

1. `adopt_separately` 策略必须至少选择一个 output；
2. UI 上应提供 source / target output 选择，或明确提供至少一个 output 的选择控件；
3. 如果未选择任何 output，前端必须提示并阻止调用接口；
4. `adopt_source` 仍必须选择 `source_output_id`；
5. `adopt_target` 仍必须选择 `target_output_id`；
6. `manual_merge` 仍必须填写 `merged_output_title` 和 `merged_content`；
7. 合并成功后仍刷新分支列表和输出版本列表。

## 验收要求

1. `/reviews` 能进入审核中心列表；
2. `/artifacts` 能进入成果库列表，不再是占位页；
3. `/artifacts/{adopted_id}` 能展示成果正文和采用信息；
4. `/statistics` 能根据后端真实字段展示概览、项目统计、模型调用、成本、审核质量、成员贡献和最近动态；
5. 分支合并 `adopt_separately` 不允许空 output 提交；
6. 未修改 backend、database；
7. 未新增后端接口；
8. 未新增大模型调用能力；
9. 如本地环境有 Node，请执行 `npm run build`；如无法执行，请在 handoff 中说明原因并完成静态检查。

## Handoff 要求

完成修复后创建：

`cursor_and_codex_chat/handoff/HANDOFF-016-FIX-frontend-review-artifact-statistics.md`

handoff 必须说明：

1. 修复了哪些文件；
2. `/artifacts` 路由如何挂载真实页面；
3. 成果库字段如何对齐后端；
4. 统计看板字段如何对齐后端；
5. `adopt_separately` 如何校验；
6. 是否执行了 `npm run build`；
7. 如未执行，说明环境原因。
