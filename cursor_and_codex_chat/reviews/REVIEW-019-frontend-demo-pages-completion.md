# REVIEW-019 前端演示页面补齐审查报告

## 1. 审查结论

需要继续修改。

Cursor 本轮已经把轻量 Vue3 前端从基础框架扩展为较完整的课程演示页面，覆盖项目空间、任务与版本、AI 生成、审核中心、成果库、统计看板和模型管理等入口。Windows 环境下执行 `npm run build` 已通过，说明当前前端语法和构建链路基本可用。

但本轮仍发现 4 个会影响真实演示流程的问题，尤其是任务详情页“另存为新版本”入口缺失、任务详情任务类型字段读取错误、AI 生成页没有选择分支导致默认生成可能失败。这些问题修复后再进入最终验收更稳妥。

## 2. Stage-19 范围遵守情况

通过。

本轮主要修改集中在 `frontend/*`，新增和增强演示页面、API 封装和菜单路由。未发现新增后端业务接口、数据库结构修改或注册功能。Stage-16 已允许成果采用、审核中心和统计看板，因此本轮页面中出现审核、成果、统计功能不再按越界处理。

## 3. 页面与接口覆盖情况

基本通过。

已覆盖登录、项目空间、任务与版本、AI 生成、输出详情、编辑、批注、审核中心、成果库、统计看板和模型管理。API 路径整体使用真实后端接口，未发现 `/api/auth/register` 调用，也未发现旧的 `/api/outputs/{output_id}/save-as` 被前端页面调用。

## 4. 构建检查

通过。

当前 Ubuntu/WSL 环境没有可用 `npm`，但通过 Windows 侧 Node 环境执行 `cd frontend && npm run build` 构建成功，输出 `✓ 1548 modules transformed` 和 `✓ built`。

## 5. 阻塞问题

### 问题 1：任务详情页没有真正实现“另存为新版本”入口

位置：`frontend/src/pages/tasks/TaskDetail.vue`

`frontend/src/api/tasks.ts` 已正确封装 `POST /api/outputs/{output_id}/save-as-new-version`，但页面中没有实际按钮或处理函数调用 `tasksApi.saveAsNewVersion()`。当前 `openSaveAsDialog()` 复用了 `adoptForm` 和 `adoptDialogVisible`，最终会进入 `handleAdopt()`，也就是“采用成果”，不是“另存为新版本”。这会导致演示中无法完成另存新版本流程，并且会误导用户。

修复建议：新增独立的 `saveAsDialogVisible`、`saveAsForm`、`handleSaveAsNewVersion()`；按真实接口提交 `output_title`、`content`、`edit_summary`、可选 `branch_id`；成功后刷新输出版本列表，并自动打开或高亮新版本；不要复用成果采用弹窗。

### 问题 2：TaskDetail 任务类型仍读取旧字段 `task_type_name`

位置：`frontend/src/pages/tasks/TaskDetail.vue`

后端 `GET /api/tasks/{task_id}` 返回字段为 `type_name`，当前页面显示 `task?.task_type_name`，会导致任务详情页任务类型显示为空。

修复建议：改为 `task?.type_name || task?.task_type_name || '-'`。

### 问题 3：AI 生成入口页没有加载任务分支，可能导致生成失败

位置：`frontend/src/pages/generate/index.vue`

该页面定义了 `selectedBranch`，但没有调用 `GET /api/tasks/{task_id}/branches` 加载分支，也没有让用户选择分支。后端生成接口虽然允许 `branch_id` 可选，但成功写入输出版本时需要合法分支；演示中建议前端明确选择 active 分支。

修复建议：进入配置生成步骤时调用 `tasksApi.getBranches(taskId)`，默认选择 active 分支；页面展示分支选择框；没有可用分支时提示用户，不要调用生成接口。

### 问题 4：AI 模型展示只读取 `display_name`，缺少兼容 fallback

位置：`frontend/src/pages/tasks/TaskDetail.vue`、`frontend/src/pages/generate/index.vue`、`frontend/src/pages/models/index.vue`

当前多处模型名称展示直接使用 `display_name`。后端当前返回该字段，但为了演示稳定性，建议兼容 `display_name || model_name || ('模型 #' + model_id)`，避免数据不完整时页面空白。

## 6. 已通过内容确认

- 项目创建请求体未使用 `course_name`；
- 创建任务请求体使用 `task_type_id`、`title`、`description`、`assignee_id`、`priority`、`due_date`，未使用 `task_name` / `task_type`；
- `priority` 中包含 `urgent`，与数据库 ENUM 一致；
- 批注 `comment_type` 使用英文枚举 `comment / suggestion / approval`；
- 批注状态使用英文枚举 `open / resolved / closed`；
- 审核评分限制在 0-10；
- 前端未调用 `/api/auth/register`；
- 未发现真实数据库密码、真实 API Key、真实 JWT Secret 或完整 `sk-` 密钥泄露；
- 未发现本轮新增后端业务接口或数据库结构修改。

## 7. 是否允许进入最终验收

暂不允许。

请先完成 `TASK-019-FIX-frontend-demo-pages-completion.md` 中列出的修复，重点保证任务详情页能够真实调用 `save-as-new-version`，并保证任务详情字段和 AI 生成流程对真实后端返回兼容。
