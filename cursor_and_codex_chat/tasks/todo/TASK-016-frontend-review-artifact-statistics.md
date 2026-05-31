# TASK-016 前端审核中心、成果库与统计看板页面

## 一、任务目标

完成前端审核中心、成果库与统计看板页面，并与 Stage-09、Stage-10、Stage-11 已实现的后端接口对接。

本阶段重点是补齐课程演示所需的审核流程、成果采用 / 分支合并入口，以及统计看板展示页面。

## 二、允许实现范围

本阶段允许实现：

1. 待审核列表页；
2. 审核详情页；
3. 完成审核弹窗；
4. `issue_tags` 选择；
5. 成果库列表页；
6. 成果详情页；
7. 采用成果入口；
8. 分支合并入口；
9. 统计看板页面；
10. 与 Stage-09 / Stage-10 / Stage-11 后端接口对接。

## 三、允许修改文件

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-016-frontend-review-artifact-statistics.md`

## 四、禁止修改文件

禁止修改：

- `backend/*`
- `database/*`
- `docs/01_数据库Schema冻结说明.md`

## 五、禁止实现内容

本阶段禁止实现：

1. 后端新接口；
2. 数据库结构修改；
3. 新的大模型调用能力。

## 六、接口对接要求

### 1. 审核中心

应对接 Stage-09 后端接口：

- `GET /api/reviews/pending`
- `GET /api/reviews/{request_id}`
- `POST /api/reviews/{request_id}/complete`
- `GET /api/issue-tags`
- 如需要提交审核入口，可复用 `POST /api/outputs/{output_id}/submit-review`，但不得把审核中心做成后端新业务。

要求：

- 待审核列表应支持分页；
- 审核详情应展示项目、任务、输出版本、提交人和完整输出内容；
- 完成审核弹窗应支持 `approved`、`rejected`、`revision_required`；
- 分数字段如有输入，应控制在 0 到 10；
- `issue_tag_ids` 应从 `GET /api/issue-tags` 选择；
- 审核完成后刷新待审核列表；
- 不得伪造审核结果。

### 2. 成果库

应对接 Stage-10 后端接口：

- `POST /api/outputs/{output_id}/adopt`
- `GET /api/projects/{project_id}/artifacts`
- `GET /api/artifacts/{adopted_id}`
- `POST /api/tasks/{task_id}/branches/merge`

要求：

- 成果库列表应能基于项目查看成果；
- 成果详情应展示完整内容；
- 采用成果入口应只调用已有后端接口；
- 分支合并入口应支持后端允许的 `merge_strategy`：
  - `adopt_source`
  - `adopt_target`
  - `manual_merge`
  - `adopt_separately`
- 不得新增后端接口；
- 不得绕过后端权限控制。

### 3. 统计看板

应对接 Stage-11 后端接口：

- `GET /api/statistics/overview`
- `GET /api/statistics/projects`
- `GET /api/statistics/model-calls`
- `GET /api/statistics/costs`
- `GET /api/statistics/reviews`
- `GET /api/statistics/member-contributions`
- `GET /api/statistics/recent-activities`

要求：

- 首页统计概览应展示核心指标卡片；
- 项目统计、模型调用统计、成本统计、审核统计、成员贡献统计、最近操作动态应分区展示；
- 如使用图表库，应保持依赖克制，优先使用 Element Plus 表格、卡片和轻量展示；
- 不得伪造统计数据；
- 接口失败应显示友好错误状态。

## 七、页面与交互要求

1. 保持 V3 Admin Vite 模板风格；
2. 复用当前 Axios request 封装；
3. 复用当前登录状态和路由守卫；
4. 页面应有 loading 状态；
5. 空数据应使用友好 Empty 状态；
6. 错误提示使用 `ElMessage` 或等价方式；
7. 不得展示后端异常堆栈；
8. 不得展示 `password_hash`、API Key、JWT Secret、数据库密码等敏感字段；
9. 不得调用不存在接口；
10. 不得把 Mock 数据作为真实业务数据。

## 八、验收重点

Cursor 完成后，Codex 将重点审查：

1. 是否遵守 Stage-16 范围；
2. 审核中心接口是否完整对接；
3. 完成审核请求体和状态值是否正确；
4. `issue_tags` 是否从后端加载；
5. 成果库列表和详情是否正确；
6. 采用成果入口是否调用真实接口；
7. 分支合并入口是否正确处理四种 `merge_strategy`；
8. 统计看板是否对接 Stage-11 真实接口；
9. 是否未新增后端接口；
10. 是否未修改数据库结构；
11. 是否没有真实密钥泄露；
12. 是否未破坏 Stage-13 至 Stage-15 已通过内容；
13. 前端构建或静态检查是否通过。

## 九、交付要求

完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-016-frontend-review-artifact-statistics.md`

handoff 中必须说明：

1. 修改了哪些前端文件；
2. 新增了哪些 API 封装；
3. 审核中心如何对接；
4. 成果库如何对接；
5. 分支合并如何对接；
6. 统计看板如何对接；
7. 是否执行了 `npm run build`；
8. 如未执行，说明原因；
9. 是否存在已知限制或待后续阶段处理事项。

