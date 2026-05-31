# TASK-013-FIX: 前端基础框架改为基于成熟 Vue3 开源模板二次开发

## 任务目标

根据 `REVIEW-013-frontend-base.md` 修复 Stage-13 阻塞问题：前端必须真正基于成熟 Vue3 开源后台模板代码底座进行二次开发，而不是仅参考 UI 风格后完全手写。

## 允许修改

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-013-FIX-frontend-base.md`

如确实需要补充跨域配置，可少量修改：

- `backend/app/main.py`

但必须在 handoff 中说明理由。

## 禁止修改

- `database/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 前端项目管理完整页面；
2. 前端任务管理完整页面；
3. 前端审核中心完整页面；
4. 前端成果库完整页面；
5. 前端统计看板完整页面；
6. 新增后端业务接口；
7. 修改后端 service / repository 业务逻辑。

## 必须修复的问题

### 1. 使用成熟 Vue3 开源后台模板作为代码底座

必须选择一个成熟、许可证兼容的 Vue3 后台模板，例如：

- vue-pure-admin；
- vue-element-plus-admin；
- Vben Admin；
- Soybean Admin；
- V3 Admin Vite；
- 或其他明确 Vue3 后台模板。

不得只写“参考 UI 风格”。必须能在 `frontend/` 中看到模板代码底座被裁剪和二次开发后的痕迹，例如模板的布局、路由、权限、样式或组件结构。

### 2. 开源合规

必须：

1. 保留模板 LICENSE / NOTICE / copyright 声明；
2. 在 `frontend/README.md` 中注明：
   - 模板名称；
   - GitHub 链接；
   - 许可证；
   - 使用范围；
   - 本项目做了哪些裁剪和二次开发；
3. 在 handoff 中说明模板来源和许可证处理；
4. 不得复制商业或非兼容许可证代码；
5. 不得把模板原项目包装成自己的原创；
6. 不得保留模板原项目 Logo、品牌名、默认业务 Mock 数据作为真实业务。

### 3. 保留 Stage-13 功能要求

基于模板改造后仍必须具备：

- Vue3 + Vite；
- Element Plus 或模板自身对应的 Vue UI 组件库；
- Pinia；
- Vue Router；
- Axios；
- `/login`；
- `/dashboard`；
- `/projects`；
- `/tasks`；
- `/reviews`；
- `/artifacts`；
- `/statistics`；
- `/models`；
- `/404`；
- 登录页对接 `POST /api/auth/login`；
- 当前用户恢复对接 `GET /api/auth/me`；
- logout 对接或兼容 `POST /api/auth/logout`；
- 后台布局：左侧导航栏、顶部用户信息栏、主内容区、退出登录；
- 路由守卫：未登录跳转 `/login`，已登录访问 `/login` 跳转 `/dashboard`。

### 4. 不得越界实现完整业务页面

项目空间、任务与版本、审核中心、成果库、统计看板、模型管理可以保留为模板风格的占位页，但不得实现完整 CRUD 或真实统计图表。

### 5. 清理空文件和无关模板内容

当前存在多个 0 字节文件和可能的无关模板残留。修复时必须：

- 删除无用 0 字节文件；或
- 明确它们的用途；
- 删除模板自带无关业务页面；
- 删除模板 Mock 数据；
- 删除模板原品牌文案；
- 将系统品牌替换为“智研协作 AI 项目质量审计系统”。

## 交付要求

完成后创建：

`cursor_and_codex_chat/handoff/HANDOFF-013-FIX-frontend-base.md`

handoff 必须说明：

1. 选用的开源模板名称；
2. 模板 GitHub 链接；
3. 模板许可证；
4. LICENSE / NOTICE 保留位置；
5. 裁剪了哪些模板内容；
6. 保留了哪些模板核心结构；
7. 如何对接 `/api/auth/login`、`/api/auth/me`；
8. 路由守卫逻辑；
9. 前端安装依赖命令；
10. 前端启动命令；
11. `npm install` / `npm run build` 执行结果；如当前环境无 Node 或无法联网，必须说明；
12. 是否修改 `backend/app/main.py`，如有说明原因；
13. 未修改 `database/*`、未修改 `docs/01_数据库Schema冻结说明.md`；
14. 未实现完整项目管理、任务管理、审核中心、成果库、统计看板页面。

## 验收标准

1. 前端确实基于成熟 Vue3 开源后台模板二次开发；
2. 开源来源和许可证说明完整；
3. 系统品牌已替换为“智研协作 AI 项目质量审计系统”；
4. 登录页、后台布局、路由守卫、Axios、Pinia 均可用；
5. 未越界实现后续业务页面；
6. 未泄露真实密钥；
7. 未修改数据库结构或 Schema 冻结文档。
