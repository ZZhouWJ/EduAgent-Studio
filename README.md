# AI-Collab-Audit-System
AI-Collab Audit System: A Git-inspired AI task management and quality audit platform for university collaborations. Track, review, and manage AI-generated content and human edits seamlessly. (Vue3 + FastAPI + MySQL)
# 智研协作 (AI-Collab Audit System) 🚀

> 面向高校项目协作的 AI 任务生成与质量审计管理系统

![Vue3](https://img.shields.io/badge/Frontend-Vue3-4FC08D?style=flat&logo=vue.js)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)
![MySQL](https://img.shields.io/badge/Database-MySQL_8.0-4479A1?style=flat&logo=mysql)
![License](https://img.shields.io/badge/License-Apache-2.0-blue.svg)

## 📖 项目简介

大模型（LLMs）已经广泛融入高校的课程设计、科研训练和创新创业项目中。然而，学生团队在使用 AI 工具时往往面临**内容散落、提示词无法复用、模型“幻觉”难辞其咎、多次修改后版本混乱**等痛点。

**“智研协作”** 并非一个简单的“大模型聊天壳子”，而是一个结合了 **Git 版本控制思想** 的人机协同内容管理平台。系统将 AI 的调用过程纳入项目管理体系，把每一次 AI 生成与人工修改看作一次“Commit”，让 AI 辅助创作变得**可管理、可追踪、可审核、可回滚**。

*(本项目为《数据库管理实务》课程结课设计项目)*

## ✨ 核心特性

- 🗂 **项目与任务空间**：以课程/竞赛项目为单位隔离数据，支持多角色（成员、负责人、指导老师）权限协同。
- 🌳 **Git 式版本管理**：每一次 AI 初稿生成、人工二次修改都将生成独立版本，构建完整的时间线与版本树，支持乐观锁防冲突。
- 🔍 **质量审计与批注**：拒绝 AI 劣质内容直接入库。支持对生成结果进行多维评分（准确性、逻辑性等）、打回修改与打标签。
- 🤖 **多模型统一调用**：一套 Prompt 跑多个模型，直观对比输出质量（初期采用 Mock 机制，支持扩展真实 API）。
- 📊 **Token 成本与用量大屏**：精细化统计不同用户、不同模型、不同项目的 Token 消耗量与估算成本。
- 🛡️ **全过程安全审计**：核心业务数据采用“软删除（Soft Delete）”，配合底层触发器与操作日志，确保内容演进的 100% 可追溯。

## 🛠️ 技术栈

本项目坚持前后端分离架构，并在后端强调**原生 SQL 的运用**，以展示关系型数据库在复杂业务场景下的掌控力。

- **前端 (Frontend)**: Vue 3 + Vite + Element Plus + Pinia + ECharts
- **后端 (Backend)**: Python 3.10+ + FastAPI (提供 RESTful API)
- **数据库 (Database)**: MySQL 8.0 (使用 PyMySQL + 原生参数化 SQL，含事务、视图与触发器)

## 📂 核心数据库实体 (ER 概览)

本系统底层包含 20+ 业务表，严格遵循第三范式 (3NF) 设计，核心实体流转如下：
`项目(Projects)` -> `任务(Tasks)` -> `模型调用(Invocations)` -> `输出版本(Outputs)` -> `审核(Reviews)` -> `最终成果(Adopted Artifacts)`

## 🚀 快速开始

*(以下为占位说明，待第一版代码提交后完善)*

### 1. 环境准备
- Node.js 18+
- Python 3.10+
- MySQL 8.0+

### 2. 数据库初始化
在 MySQL 中运行 `database/01_create_tables.sql` 与 `02_insert_mock_data.sql` 完成建库建表与测试数据导入。

### 3. 启动后端 (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
