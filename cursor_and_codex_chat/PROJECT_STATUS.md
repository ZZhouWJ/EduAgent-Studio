# 项目当前状态

## 当前阶段

Stage-01 数据库脚本：已通过 Codex 第三轮静态审查。
当前进入：Stage-02 FastAPI 后端基础框架。

说明：由于当前 Codex 所在 Ubuntu / WSL 环境无法直接访问 Windows MySQL，Stage-01 实际 MySQL 顺序导入验证将在 Windows MySQL 环境中后续补做，不阻塞 Stage-02。

## 当前技术栈

- 前端：Vue3 + Vite + Element Plus + Pinia + Vue Router + ECharts
- 后端：Python FastAPI
- 数据库：MySQL 8.0
- 数据库访问：参数化 SQL / Repository 层
- 模型调用：Mock ModelAdapter + 可选真实模型 API

## 已完成内容

- docs/ 四份 AI 防幻觉控制文档
- database/ 7 个 SQL 文件
- 27 张表
- 索引
- 初始化数据
- 视图
- 触发器
- 存储过程
- 测试 SQL
- Stage-01 R3 静态审查通过

## 未完成内容

- Windows MySQL 环境下补做 Stage-01 SQL 顺序导入验证
- Stage-02 后端基础框架
- Stage-03 登录与权限
- Stage-04 项目空间管理
- Stage-05 任务与版本管理
- Stage-06 提示词模板
- Stage-07 模型调用
- Stage-08 人工编辑与乐观锁
- Stage-09 审核中心
- Stage-10 成果库
- Stage-11 统计看板
- Stage-12 测试与报告截图
