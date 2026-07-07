# EduAgent Studio - Claude Code 项目指南

## 项目概述

智学工坊 EduAgent Studio 是中国软件杯 A3 赛题参赛作品——基于大模型的个性化资源生成与学习多智能体系统。

## 关键文件

- **项目状态跟踪**: `docs/PROJECT_STATUS.md` - ⚠️ **每次工作前必须读取并更新**
- **架构文档**: `docs/ARCHITECTURE.md`
- **智能体设计**: `docs/多智能体设计.md`
- **赛题要求**: `docs/A3当前实现状态与缺口清单.md`
- **竞品分析**: `docs/竞品分析与创新点.md`

## 工作流程

### 1. 开始工作时
1. 读取 `docs/PROJECT_STATUS.md` 了解当前项目状态
2. 查看 `docs/A3当前实现状态与缺口清单.md` 了解赛题缺口
3. 根据优先级选择任务

### 2. 完成工作后
1. 更新 `docs/PROJECT_STATUS.md` 相关条目的状态
2. 在版本历史中添加更新记录
3. 如有必要，更新其他相关文档

## 赛题要求优先级

| 优先级 | 要求 | 数量 |
|--------|------|------|
| P0（必做） | 核心功能要求 | 16项 |
| P1（加分） | 智能辅导/效果评估 | 2项 |
| P2（文档） | 系统开发/测试文档 | 3项 |

## 技术栈

- **前端**: React 18 + Vite + TypeScript + Tailwind v4 + shadcn/ui
- **后端**: FastAPI + Pydantic + SQLAlchemy + MySQL
- **多智能体**: LangGraph + LangChain Core
- **LLM**: 统一 Gateway（Mock/OpenAI/Qwen/DeepSeek/MiniMax）
- **知识库**: BM25 本地检索（不依赖外部 Embedding API）

## 快速启动

```bash
# 后端
cd backend && uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm run dev
```

## 关键约定

1. **不破坏现有功能**：修改前先验证不影响现有流程
2. **更新 PROJECT_STATUS.md**：完成工作后必须更新项目状态文件
3. **保持文档同步**：代码变更后同步更新相关文档
4. **提交前检查**：确保 TypeScript 编译通过（`npm run build`）
