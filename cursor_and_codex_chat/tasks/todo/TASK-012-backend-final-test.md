# TASK-012: 后端整体联调、运行验证与课程报告素材整理

## 任务目标

完成后端整体联调、运行验证与课程报告素材整理，为课程验收和后续展示准备可复现的后端运行说明、测试脚本和报告材料。

## 允许实现内容

1. 后端依赖整理；
2. 环境变量样例文件；
3. 启动说明；
4. API 路由清单；
5. 后端整体 `py_compile` 检查；
6. 关键接口 `curl` 测试脚本；
7. 数据库连接说明；
8. 测试报告素材整理；
9. `README` 后端运行部分补充。

## 禁止实现内容

1. 新业务模块；
2. 前端页面；
3. 数据库结构修改。

## 建议允许修改文件

- `backend/requirements.txt`
- `backend/.env.example`
- `backend/README.md`
- `backend/scripts/test_api_curl.sh`
- `backend/scripts/py_compile_check.sh`
- `README.md`
- `cursor_and_codex_chat/handoff/HANDOFF-012-backend-final-test.md`

如实际项目中已有等价文件或目录，请优先沿用现有结构，不要重复创建相同用途文件。

## 明确禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 验收要求

1. `requirements.txt` 中后端依赖清晰、必要、无明显多余大型依赖。
2. 环境变量样例文件不包含真实密码、真实 Token、真实 API Key。
3. 启动说明包含依赖安装、环境变量配置、启动命令和访问地址。
4. API 路由清单覆盖当前已实现后端接口。
5. 提供可执行的整体 `py_compile` 检查命令或脚本。
6. 提供关键接口 `curl` 测试脚本，覆盖健康检查、登录、项目、任务、模型调用、统计等核心路径。
7. 数据库连接说明明确 Windows MySQL / WSL 环境限制和配置方式。
8. 测试报告素材包含检查项、执行命令、预期结果和截图/记录建议。
9. 不新增业务逻辑，不修改数据库结构，不实现前端页面。

## 交付要求

完成后创建：

`cursor_and_codex_chat/handoff/HANDOFF-012-backend-final-test.md`

handoff 中必须说明：

1. 修改了哪些文件；
2. 依赖安装命令；
3. 后端启动命令；
4. `py_compile` 检查命令与结果；
5. `curl` 测试脚本使用方式；
6. 数据库连接配置方式；
7. 未实现新业务模块、未修改前端、未修改数据库结构的确认。
