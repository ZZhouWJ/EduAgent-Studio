# AI Coding 工具使用说明

> 本文档介绍 EduAgent Studio 项目（A3 赛题：基于大模型的个性化资源生成与学习多智能体系统开发）中所使用的 AI Coding 工具及其规范。

---

## 1. AI Coding 工具使用说明

### 1.1 使用的 AI Coding 工具

| 工具 | 定位 | 说明 |
|------|------|------|
| **Cursor IDE** | 主要工具 | 核心开发环境，内置 Composer 和 Agent 模式，支持全项目代码编辑 |
| **Claude** | 辅助工具 | 复杂架构设计、代码审查、疑难问题分析 |
| **ChatGPT** | 辅助工具 | 快速原型验证、文档生成、简单逻辑实现 |

### 1.2 使用场景

| 场景 | 适用工具 | 说明 |
|------|----------|------|
| 需求分析和文档生成 | Cursor + ChatGPT | 快速生成结构化文档、需求分析 |
| 代码架构设计 | Cursor + Claude | 多文件协同设计、架构评审 |
| 前后端代码实现 | Cursor Composer | 多文件同步修改、重构、大规模代码生成 |
| Bug 修复和优化 | Cursor Agent | 独立诊断和修复、代码优化建议 |
| 单元测试生成 | Cursor | 根据代码结构生成测试用例 |

### 1.3 Cursor 使用方式详解

#### Cursor Composer（多文件协同编辑）

- **适用场景**：跨多个文件的重构、批量代码生成、架构调整
- **优势**：可以同时打开项目中的多个文件，保持上下文一致
- **典型用法**：
  - 大规模重构：同时修改前后端接口定义
  - 新功能开发：生成 Controller → Service → Repository 全链路代码
  - 规范迁移：将 mock 数据替换为真实数据库调用

#### Cursor Agent（独立任务执行）

- **适用场景**：独立可闭环的任务，如 Bug 修复、代码审查、文档生成
- **优势**：自主推理、工具调用、多轮迭代直到任务完成
- **典型用法**：
  - "将 agent_service.py 中的 mock 数据替换为真实数据库查询"
  - "审查并优化 Repository 层的错误处理"
  - "生成数据初始化脚本"

#### Cursor Rules（项目规范指导）

- **适用场景**：确保 AI 生成代码符合项目架构规范
- **配置方式**：在 `.cursor/rules/` 目录下编写 `.mdc` 规则文件
- **典型效果**：AI 在生成代码时自动遵循前后端分离、Repository 模式等规范

---

## 2. Cursor Rules 规范

项目在 `.cursor/rules/` 目录下定义了多项开发规范，主要规则如下：

### 2.1 架构分层规范

| 规则 | 说明 |
|------|------|
| **前后端分离** | 前端（Vue/TypeScript）与后端（Python/FastAPI）严格分离，不跨层直接调用 |
| **数据库操作走 Repository 层** | 所有数据库操作统一通过 Repository 层，不在 Service 或 API 层直接操作 ORM |
| **FastAPI 路由不直接操作数据库** | API 层只负责请求解析和响应组装，逻辑下沉到 Service 层 |

### 2.2 前端规范

| 规则 | 说明 |
|------|------|
| **Token 管理统一走 userStore** | 前端不直接操作 localStorage，统一通过 userStore 管理认证状态 |
| **API 错误统一处理** | 使用统一的错误拦截器处理 API 异常，用户只看到友好的错误提示 |

### 2.3 后端规范

| 规则 | 说明 |
|------|------|
| **Service 层处理业务逻辑** | 业务规则、校验、编排逻辑放在 Service 层 |
| **Repository 层封装数据访问** | 数据库查询、关联、事务控制在 Repository 层 |
| **API 错误码统一** | 所有 API 错误使用统一的错误码和格式返回 |

---

## 3. 本轮增量开发（2026-06-12）

本轮开发由 Cursor Agent 驱动，完成从 mock 数据到真实数据库的全面改造。

### 3.1 主要改造内容

| 改造项 | 文件/范围 | 说明 |
|--------|----------|------|
| 移除 mock 数据 | `agent_service.py` | 删除 `_MOCK_KNOWLEDGE_POINTS` 等硬编码数据 |
| 真实数据库查询 | 多个 Service 层 | 将 mock 调用替换为 Repository 层查询 |
| 画像更新闭环 | feedback 提交流程 | 用户反馈触发学生画像实时更新 |
| 数据初始化 | 数据库初始化脚本 | 补充学生画像初始数据 |
| Markdown 渲染 | 前端组件 | 使用 `marked` 库替代原生渲染 |

### 3.2 改造前后对比

#### 改造前（Mock 数据）

```python
# agent_service.py (改造前)
_MOCK_KNOWLEDGE_POINTS = [
    {"id": 1, "name": "一元二次方程", "mastery": 0.6},
    {"id": 2, "name": "函数图像", "mastery": 0.3},
]
```

#### 改造后（真实数据库查询）

```python
# agent_service.py (改造后)
from app.repositories.agent_repository import AgentRepository

class AgentService:
    def __init__(self):
        self.agent_repo = AgentRepository()

    def get_knowledge_points(self, student_id: int):
        return self.agent_repo.get_student_knowledge_mastery(student_id)
```

---

## 4. Cursor 在本项目中的贡献

### 4.1 代码生成效率提升

| 贡献项 | 具体效果 |
|--------|----------|
| Repository 层快速生成 | 基于数据库模型自动生成 CRUD 基础代码 |
| 类型补全 | 前端组件 Props 和 API 响应类型的自动推导 |
| 测试用例生成 | 根据函数签名和边界条件生成单元测试 |

### 4.2 架构规范化

| 贡献项 | 具体效果 |
|--------|----------|
| API 与 Repository 分离 | 批量重构确保所有 API 层通过 Service 调用 Repository |
| 错误处理统一 | 全局异常拦截器 + 统一错误响应格式 |
| 前端状态管理规范化 | userStore 统一管理 Token，避免散落 localStorage 操作 |

### 4.3 文档与维护

| 贡献项 | 具体效果 |
|--------|----------|
| 批量文档生成 | API 文档、数据字典、开发规范文档批量生成 |
| 文档一致性维护 | 代码变更时同步更新相关文档 |
| README 与快速开始 | 新成员可通过文档快速上手项目 |

### 4.4 典型工作流示例

```
需求输入 → Cursor Composer 多文件设计 → Cursor Agent 逐模块实现 → Cursor 审查优化 → Git 提交
```

1. **需求分析**：使用 ChatGPT 快速生成需求文档初稿
2. **架构设计**：Claude 评审架构方案，Cursor Composer 生成多文件骨架
3. **编码实现**：Cursor Agent 驱动开发，逐模块完成并自测
4. **代码审查**：Cursor + Claude 双重审查，确保规范遵循
5. **文档同步**：Cursor 自动更新相关文档，保持一致性

---

*本文档由 Cursor AI 辅助生成，最后更新：2026-06-12*
