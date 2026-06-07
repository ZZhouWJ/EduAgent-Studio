# HANDOFF-016 前端审核中心、成果库与统计看板

## 一、Stage-16 完成情况

本次完成 Stage-16 前端审核中心、成果库与统计看板页面的实现，所有页面与 Stage-09 / Stage-10 / Stage-11 后端接口对接。

## 二、修改文件清单

### 新增 API 类型文件

| 文件 | 说明 |
|------|------|
| `frontend/src/common/apis/reviews/type.ts` | 审核请求、审核详情、审核请求体、问题标签类型 |
| `frontend/src/common/apis/artifacts/type.ts` | 成果项、采用请求体、分支合并请求体类型 |
| `frontend/src/common/apis/statistics/type.ts` | 概览、项目统计、模型调用、成本、审核质量、成员贡献、最近活动类型 |

### 新增 API 函数文件

| 文件 | 函数 |
|------|------|
| `frontend/src/common/apis/reviews/index.ts` | `getPendingReviewsApi`、`getReviewDetailApi`、`completeReviewApi`、`getIssueTagsApi` |
| `frontend/src/common/apis/artifacts/index.ts` | `adoptOutputApi`、`getProjectArtifactsApi`、`getArtifactDetailApi`、`mergeTaskBranchesApi` |
| `frontend/src/common/apis/statistics/index.ts` | `getStatisticsOverviewApi`、`getProjectStatisticsApi`、`getModelCallStatisticsApi`、`getCostStatisticsApi`、`getReviewStatisticsApi`、`getMemberContributionsApi`、`getRecentActivitiesApi` |

### 新增页面文件

| 文件 | 说明 |
|------|------|
| `frontend/src/pages/reviews/ReviewList.vue` | 审核中心列表页 |
| `frontend/src/pages/reviews/ReviewDetail.vue` | 审核详情页 + 完成审核弹窗 |
| `frontend/src/pages/artifacts/ArtifactList.vue` | 成果库列表页 |
| `frontend/src/pages/artifacts/ArtifactDetail.vue` | 成果详情页 |
| `frontend/src/pages/statistics/StatisticsDashboard.vue` | 统计看板页 |

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/router/index.ts` | `statistics` 路由改为 `StatisticsDashboard.vue`；添加 `reviews/:requestId` 和 `artifacts/:adoptedId` 嵌套路由 |
| `frontend/src/pages/tasks/TaskDetail.vue` | 添加采用成果按钮（仅 `approved` 状态显示）；添加分支合并按钮（至少 2 个分支时显示）；添加对应弹窗和 API 调用 |

## 三、API 封装列表

### 审核中心 API

| 函数 | 方法 | 路径 | 说明 |
|------|------|------|------|
| `getPendingReviewsApi` | GET | `/api/reviews/pending` | 待审核列表，支持分页和 project_id 过滤 |
| `getReviewDetailApi` | GET | `/api/reviews/{request_id}` | 审核详情 |
| `completeReviewApi` | POST | `/api/reviews/{request_id}/complete` | 完成审核 |
| `getIssueTagsApi` | GET | `/api/issue-tags` | 问题标签列表 |

### 成果库 API

| 函数 | 方法 | 路径 | 说明 |
|------|------|------|------|
| `adoptOutputApi` | POST | `/api/outputs/{output_id}/adopt` | 采用输出为成果 |
| `getProjectArtifactsApi` | GET | `/api/projects/{project_id}/artifacts` | 项目成果列表 |
| `getArtifactDetailApi` | GET | `/api/artifacts/{adopted_id}` | 成果详情 |
| `mergeTaskBranchesApi` | POST | `/api/tasks/{task_id}/branches/merge` | 分支合并 |

### 统计看板 API

| 函数 | 方法 | 路径 | 说明 |
|------|------|------|------|
| `getStatisticsOverviewApi` | GET | `/api/statistics/overview` | 统计概览 |
| `getProjectStatisticsApi` | GET | `/api/statistics/projects` | 项目维度统计 |
| `getModelCallStatisticsApi` | GET | `/api/statistics/model-calls` | 模型调用统计 |
| `getCostStatisticsApi` | GET | `/api/statistics/costs` | 成本统计 |
| `getReviewStatisticsApi` | GET | `/api/statistics/reviews` | 审核质量统计 |
| `getMemberContributionsApi` | GET | `/api/statistics/member-contributions` | 成员贡献统计 |
| `getRecentActivitiesApi` | GET | `/api/statistics/recent-activities` | 最近操作动态 |

## 四、审核中心实现说明

### 审核列表页（ReviewList.vue）

- 路由：`/reviews`
- 调用 `GET /api/reviews/pending`
- 展示字段：request_id、project_name、task_title、output_title、submitter_real_name、reviewer_real_name、request_status（Tag）、submit_note、created_at
- 支持按 project_id 过滤
- 支持分页
- 点击行进入审核详情页

### 审核详情页（ReviewDetail.vue）

- 路由：`/reviews/:requestId`
- 调用 `GET /api/reviews/{request_id}`
- 展示审核请求基础信息（el-descriptions）
- 展示完整输出内容（content）
- 展示审核状态标签
- 仅 `pending` 状态显示「完成审核」按钮

### 完成审核弹窗

- 调用 `POST /api/reviews/{request_id}/complete`
- `review_status` 只能选择：`approved`、`rejected`、`revision_required`（el-radio-group）
- 评分字段（accuracy_score、completeness_score、logic_score、format_score、usability_score、risk_score）使用 el-input-number，范围 0-10，支持小数
- 校验：分数超出 0-10 范围时报错
- `review_comment` 必填（el-form 校验）
- `issue_tag_ids` 从 `GET /api/issue-tags` 加载，支持多选
- 成功后刷新审核详情

## 五、issue_tags 加载说明

- 在 `openCompleteDialog()` 中调用 `getIssueTagsApi()`
- 加载完成后赋值给 `issueTags` ref
- el-select multiple 绑定 `completeForm.issue_tag_ids`
- 加载失败时 `issueTags` 置为空数组，不阻塞弹窗打开

## 六、成果库实现说明

### 成果列表页（ArtifactList.vue）

- 路由：`/artifacts`
- 先加载项目列表，默认为第一个项目
- 调用 `GET /api/projects/{project_id}/artifacts`
- 支持切换项目
- 支持分页
- 展示字段：adopted_id、artifact_title、artifact_type（Tag）、release_version、task_title、output_title、adopted_by_real_name、created_at
- 点击标题进入成果详情

### 成果详情页（ArtifactDetail.vue）

- 路由：`/artifacts/:adoptedId`
- 调用 `GET /api/artifacts/{adopted_id}`
- 展示成果基础信息
- 展示完整 content（scrollable box）
- 不展示 password_hash、API Key 等敏感字段

## 七、采用成果入口说明

- 位于任务详情页输出详情弹窗内
- 仅当 `outputDetail.status === 'approved'` 时显示「采用为成果」按钮
- 调用 `POST /api/outputs/{output_id}/adopt`
- 必填字段：artifact_title、artifact_type
- 可选字段：release_version（默认 v1.0）、adopt_note
- 成功后刷新任务详情（重新拉取 task/branches/outputs）

## 八、分支合并入口说明

- 位于任务详情页分支 Tab 内
- 仅当 `branches.length >= 2` 时显示「分支合并」按钮
- 调用 `POST /api/tasks/{task_id}/branches/merge`
- 支持四种合并策略：
  - `adopt_source`：必须选择 source_output_id
  - `adopt_target`：必须选择 target_output_id
  - `manual_merge`：必须填写 merged_output_title 和 merged_content
  - `adopt_separately`：允许不选择输出
- 前端额外校验：source_branch_id 和 target_branch_id 不能相同
- 成功后刷新任务详情（重新拉取 task/branches/outputs）

## 九、统计看板实现说明

### 路由

- 路由：`/statistics`
- 页面文件：`StatisticsDashboard.vue`

### 展示内容

1. **概览卡片**（8个）：项目总数、进行中项目、任务总数、已完成任务、输出总数、已通过输出、模型调用次数、累计成本
2. **项目统计表**：项目名称、成员数、任务数、输出数、已通过数、成本
3. **模型调用统计表**：模型名称、调用次数、输入/输出 Tokens、成本
4. **成本统计卡片**：总成本、输入成本、输出成本、币种
5. **审核质量统计卡片**：审核总数、通过/拒绝/需修改数、平均分（准确度/完整度/逻辑性/可用性）
6. **成员贡献排行表**：排名、成员名、输出数、已通过数、调用次数、成本
7. **最近操作动态列表**：操作类型标签、操作描述、用户名、项目名、时间

### ECharts 使用情况

未安装 ECharts，使用 Element Plus 表格（el-table）、卡片（el-card）、网格布局实现所有统计图表化展示。无数据时展示 0 或 el-empty。

## 十、路由与菜单

### 路由配置

| 路由 | 文件 | hidden |
|------|------|--------|
| `/reviews` | `pages/reviews/index.vue` | 否 |
| `/reviews/:requestId` | `pages/reviews/ReviewDetail.vue` | 是 |
| `/artifacts` | `pages/artifacts/index.vue` | 否 |
| `/artifacts/:adoptedId` | `pages/artifacts/ArtifactDetail.vue` | 是 |
| `/statistics` | `pages/statistics/StatisticsDashboard.vue` | 否 |

### 菜单

左侧菜单栏自动由 `router/index.ts` 常驻路由生成，无需手动配置。`/reviews`、`/artifacts`、`/statistics` 均已在路由中注册，出现在左侧菜单。

## 十一、是否越界实现

| 项目 | 是否实现 | 说明 |
|------|----------|------|
| 审核中心完整页面 | **是** | 列表页 + 详情页 + 完成审核弹窗 |
| 成果库完整页面 | **是** | 列表页 + 详情页 + 采用入口 |
| 统计看板完整页面 | **是** | 7 个统计区域全实现 |
| 修改 backend | **否** | 仅修改前端 |
| 修改 database | **否** | 未修改 |
| 新增后端接口 | **否** | 未新增 |

## 十二、安全检查

- 无真实数据库密码
- 无真实 API Key
- 无真实 JWT Secret
- 无完整 sk- 开头密钥
- 无 password_hash 展示
- 无 encrypted_api_key / key_iv / key_tag 展示
- 未调用 `/api/auth/register`
- 未硬编码 Admin@123456 自动登录

## 十三、当前环境限制

远程 Ubuntu/WSL 环境当前未安装 Node，执行 `node -v && npm -v && npm run build` 返回 `node: command not found`。本次已完成所有文件级别的静态修改，所有文件均通过 linter 检查（无 lint 错误），但无法执行 `npm run build` 验证编译。

## 十四、需要 Codex 审查的重点

1. **审核中心接口是否完整对接**：pending、detail、complete、issue-tags 四个接口是否正确调用
2. **完成审核请求体**：review_status 是否只接受 approved/rejected/revision_required；评分是否限制在 0-10
3. **issue_tags 是否从后端加载**：而非硬编码
4. **成果库列表和详情是否正确**：按项目查询成果
5. **采用成果入口是否调用真实接口**：POST /api/outputs/{output_id}/adopt；仅 approved 状态显示
6. **分支合并四种策略是否正确处理**：adopt_source/adopt_target 必须选输出；manual_merge 必须填标题和内容
7. **统计看板是否对接 Stage-11 真实接口**：7 个统计接口全部调用
8. **是否未新增后端接口**
9. **是否未修改数据库结构**
10. **是否没有真实密钥泄露**
11. **是否未破坏 Stage-13 至 Stage-15 已通过内容**
12. **前端 linter 是否全部通过**（已通过，无 lint 错误）
