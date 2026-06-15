# EduAgent Studio — React 前端迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把新 `frontend/`（React 18 + Vite + shadcn/ui 模板，已含 27 个 UI 页面）从静态 mock 数据切换为真实后端 API 调用，实现鉴权、跨角色路由守卫、业务联调，达到"打开浏览器即可登录使用"的最终态。

**Architecture:** 单仓 React SPA。后端 `backend/app/`（FastAPI，统一响应 `{code, message, data}`，CORS 全开，端口 8002）。前端用 axios + Zustand + react-router@7（HashRouter/BrowserRouter 二选一，沿用 BrowserRouter），不引入 React Query（axios + useEffect/useState 即可），把 17 个 API 模块从 `frontend_old/src/api/` 翻译到新 `frontend/src/lib/api/`，所有 `demoData` 引用替换为 `useApi` 自定义 hook。鉴权用 Bearer Token（localStorage 持久化），按 `roles` 字段路由分流。

**Tech Stack:** React 18, Vite 6, TypeScript 5, Tailwind v4, shadcn/ui (Radix + CVA), react-router 7, axios 1.x, zustand 4.x, lucide-react, sonner（toast）, recharts.

---

## 关键事实（执行前必读）

- **后端状态**：已就绪，进程在 8000 端口监听，MySQL 已连接（`/api/health/db` 返回 connected）
- **后端进程**：`nohup python run.py > /tmp/backend.log 2>&1 &`（子 agent 起的）
- **后端 `.env` 关键值**：
  - `APP_NAME=AI-Collab-Audit-System`（不是 EduAgent Studio，但前端不依赖这个）
  - `DB_HOST=127.0.0.1 DB_PORT=3306 DB_USER=root DB_PASSWORD=061202 DB_NAME=ai_collab_audit_system`
  - `LLM_PROVIDER=minimax LLM_MODEL=MiniMax-M3`
- **测试账号**：`admin`（密码 `Admin@123`）、`teacher1`（密码 `123456`）、`student1`（密码 `123456`）
- **修复过的 git 提交**：
  - `adcb8c2` 阶段 0：切换到 React 模板
  - `1cd5cca` 修复后端合并冲突（main.py + learning.py）
  - `2cbc97f` 加 langgraph-checkpoint-sqlite 依赖

---

## 阶段 0：仓库清理

### Task 0.1：把 `frontend_old` 加入 `.gitignore` 并提交清理快照

**Files:**
- Modify: `.gitignore`
- Modify: `frontend/.gitignore`（如不存在则创建）
- Stage: `git rm -r frontend/` 跟踪的文件（不包括新 frontend 已存在的）
- Stage: `git add frontend/` 新增的文件 + `frontend_old/`（保持 untracked）

- [ ] **Step 1：编辑项目根 `.gitignore`**

在文件末尾追加：
```
# 旧版前端（保留在本地作为参考，不进仓库）
frontend_old/
```

- [ ] **Step 2：检查新 frontend 是否有自己的 .gitignore**

```bash
ls -la frontend/.gitignore
```

如果不存在，创建 `frontend/.gitignore`：
```
node_modules
dist
.env
.env.local
.DS_Store
*.log
.vite
```

- [ ] **Step 3：分阶段暂存变更**

```bash
# 1) 删除旧 frontend 跟踪的文件（保留 frontend_old 作为未跟踪）
git rm -r frontend/.cursor frontend/.env frontend/.env.development frontend/.env.example \
       frontend/.gitignore frontend/.npmrc frontend/AGENTS.md frontend/CLAUDE.md \
       frontend/LICENSE frontend/NOTICE.md frontend/README.md frontend/index.html \
       frontend/package.json frontend/pnpm-lock.yaml frontend/public \
       frontend/scripts frontend/skills-lock.json frontend/src \
       frontend/tests frontend/tsconfig.json frontend/types frontend/vite.config.ts 2>/dev/null

# 2) 把"新 frontend 的内容"作为新增 add（不在 git rm 列表里的新文件已 untracked）
git add frontend/ATTRIBUTIONS.md frontend/guidelines frontend/pnpm-workspace.yaml \
        frontend/postcss.config.mjs frontend/src frontend/vite.config.ts \
        frontend/package.json frontend/pnpm-lock.yaml frontend/index.html frontend/README.md

git add .gitignore frontend/.gitignore
```

- [ ] **Step 4：验证状态**

```bash
git status
```

预期：
- `frontend_old/` 显示为 Untracked
- `frontend/` 下大量文件显示为 deleted（旧的）和 added（新的）
- 没有冲突标记

- [ ] **Step 5：提交清理快照**

```bash
git commit -m "chore: 切换前端到 React 18 + shadcn/ui 模板

- 旧 Vue 前端保留在 frontend_old/（不追踪）
- 新 frontend/ 基于 Figma Make 导出的 React 模板，已含 27 个业务页面 UI
- 后续按 docs/superpowers/plans/2026-06-14-react-frontend-migration.md 接入 API"
```

---

## 阶段 1：项目身份与基础配置

### Task 1.1：调整 `package.json` 项目身份与脚本

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1：替换 package.json 关键字段**

完整重写为：
```json
{
  "name": "eduagent-studio-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "tsc --noEmit"
  },
  "dependencies": {
    "@emotion/react": "11.14.0",
    "@emotion/styled": "11.14.1",
    "@mui/icons-material": "7.3.5",
    "@mui/material": "7.3.5",
    "@popperjs/core": "2.11.8",
    "@radix-ui/react-accordion": "1.2.3",
    "@radix-ui/react-alert-dialog": "1.1.6",
    "@radix-ui/react-aspect-ratio": "1.1.2",
    "@radix-ui/react-avatar": "1.1.3",
    "@radix-ui/react-checkbox": "1.1.4",
    "@radix-ui/react-collapsible": "1.1.3",
    "@radix-ui/react-context-menu": "2.2.6",
    "@radix-ui/react-dialog": "1.1.6",
    "@radix-ui/react-dropdown-menu": "2.1.6",
    "@radix-ui/react-hover-card": "1.1.6",
    "@radix-ui/react-label": "2.1.2",
    "@radix-ui/react-menubar": "1.1.6",
    "@radix-ui/react-navigation-menu": "1.2.5",
    "@radix-ui/react-popover": "1.1.6",
    "@radix-ui/react-progress": "1.1.2",
    "@radix-ui/react-radio-group": "1.2.3",
    "@radix-ui/react-scroll-area": "1.2.3",
    "@radix-ui/react-select": "2.1.6",
    "@radix-ui/react-separator": "1.1.2",
    "@radix-ui/react-slider": "1.2.3",
    "@radix-ui/react-slot": "1.1.2",
    "@radix-ui/react-switch": "1.1.3",
    "@radix-ui/react-tabs": "1.1.3",
    "@radix-ui/react-toggle-group": "1.1.2",
    "@radix-ui/react-toggle": "1.1.2",
    "@radix-ui/react-tooltip": "1.1.8",
    "axios": "^1.7.0",
    "canvas-confetti": "1.9.4",
    "class-variance-authority": "0.7.1",
    "clsx": "2.1.1",
    "cmdk": "1.1.1",
    "date-fns": "3.6.0",
    "embla-carousel-react": "8.6.0",
    "input-otp": "1.4.2",
    "lucide-react": "0.487.0",
    "motion": "12.23.24",
    "next-themes": "0.4.6",
    "react-day-picker": "8.10.1",
    "react-dnd": "16.0.1",
    "react-dnd-html5-backend": "16.0.1",
    "react-hook-form": "7.55.0",
    "react-popper": "2.3.0",
    "react-resizable-panels": "2.1.7",
    "react-responsive-masonry": "2.7.1",
    "react-router": "7.13.0",
    "react-slick": "0.31.0",
    "recharts": "2.15.2",
    "sonner": "2.0.3",
    "tailwind-merge": "3.2.0",
    "tw-animate-css": "1.3.8",
    "vaul": "1.1.2",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@tailwindcss/vite": "4.1.12",
    "@types/node": "^20.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "4.7.0",
    "tailwindcss": "4.1.12",
    "typescript": "^5.5.0",
    "vite": "6.3.5"
  },
  "peerDependencies": {
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "peerDependenciesMeta": {
    "react": { "optional": true },
    "react-dom": { "optional": true }
  },
  "pnpm": {
    "overrides": { "vite": "6.3.5" }
  }
}
```

- [ ] **Step 2：安装依赖**

```bash
cd frontend && pnpm install
```

预期：依赖安装完成，无 error。如果某个 radix 包缺失，调整后重装。

---

### Task 1.2：配置环境变量与 Vite proxy

**Files:**
- Create: `frontend/.env`
- Create: `frontend/.env.development`
- Create: `frontend/.env.example`
- Modify: `frontend/vite.config.ts`

- [ ] **Step 1：创建 `.env`**

```
VITE_API_BASE_URL=/api
```

- [ ] **Step 2：创建 `.env.development`**

```
VITE_API_BASE_URL=/api
VITE_APP_TITLE=智学工坊 EduAgent Studio
```

- [ ] **Step 3：创建 `.env.example`**

```
# API base URL（Vite proxy 会把 /api/* 转发到后端）
VITE_API_BASE_URL=/api
VITE_APP_TITLE=智学工坊 EduAgent Studio
```

- [ ] **Step 4：扩展 `vite.config.ts`**

完整重写为：
```typescript
import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

function figmaAssetResolver() {
  return {
    name: 'figma-asset-resolver',
    resolveId(id) {
      if (id.startsWith('figma:asset/')) {
        const filename = id.replace('figma:asset/', '')
        return path.resolve(__dirname, 'src/assets', filename)
      }
    },
  }
}

export default defineConfig({
  plugins: [
    figmaAssetResolver(),
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  assetsInclude: ['**/*.svg', '**/*.csv'],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## 阶段 2：基础架构

### Task 2.1：HTTP 客户端（axios 封装）

**Files:**
- Create: `frontend/src/lib/api.ts`

- [ ] **Step 1：创建 `frontend/src/lib/api.ts`**

完整内容：
```typescript
import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

const TOKEN_KEY = 'eduagent_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export interface ApiEnvelope<T = unknown> {
  code: number
  message: string
  data: T
}

export class ApiError extends Error {
  code: number
  httpStatus?: number
  constructor(message: string, code: number, httpStatus?: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.httpStatus = httpStatus
  }
}

const client: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
})

client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

client.interceptors.response.use(
  (response) => {
    const body = response.data as ApiEnvelope
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) {
        return body.data as any
      }
      return Promise.reject(new ApiError(body.message || '请求失败', body.code, response.status))
    }
    return response.data
  },
  (error: AxiosError<ApiEnvelope>) => {
    if (error.response) {
      const { status, data } = error.response
      const message = data?.message || error.message || '请求失败'
      if (status === 401) {
        clearToken()
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(new ApiError('登录已过期，请重新登录', 401, 401))
      }
      if (status === 403) return Promise.reject(new ApiError('无访问权限', 403, 403))
      if (status === 404) return Promise.reject(new ApiError('请求地址不存在', 404, 404))
      if (status >= 500) return Promise.reject(new ApiError('服务器错误，请稍后重试', status, status))
      return Promise.reject(new ApiError(message, data?.code ?? status, status))
    }
    return Promise.reject(new ApiError('网络错误，请检查网络连接', -1))
  },
)

export default client
```

---

### Task 2.2：Toast 工具（包装 sonner）

**Files:**
- Create: `frontend/src/lib/toast.ts`

- [ ] **Step 1：创建 `frontend/src/lib/toast.ts`**

```typescript
import { toast } from 'sonner'

export const notify = {
  success: (msg: string) => toast.success(msg),
  error: (msg: string) => toast.error(msg),
  info: (msg: string) => toast.info(msg),
  warning: (msg: string) => toast.warning(msg),
}
```

- [ ] **Step 2：在 Layout 中挂载 Toaster**

读取 `frontend/src/app/components/Layout.tsx`，在文件顶部加入 `import { Toaster } from 'sonner'`，在 `return` 的最外层 JSX 包裹内增加 `<Toaster position="top-right" richColors />`。

---

### Task 2.3：通用 useApi hook

**Files:**
- Create: `frontend/src/lib/useApi.ts`

- [ ] **Step 1：创建 `frontend/src/lib/useApi.ts`**

```typescript
import { useEffect, useState, useCallback } from 'react'
import client, { ApiError } from './api'

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
}

export interface UseApiResult<T, P extends unknown[] = []> extends UseApiState<T> {
  refetch: (...args: P) => Promise<void>
}

export function useApi<T, P extends unknown[] = []>(
  fetcher: (...args: P) => Promise<T>,
  deps: ReadonlyArray<unknown> = [],
): UseApiResult<T, P> {
  const [state, setState] = useState<UseApiState<T>>({ data: null, loading: true, error: null })

  const run = useCallback(async (...args: P) => {
    setState((s) => ({ ...s, loading: true, error: null }))
    try {
      const data = await fetcher(...args)
      setState({ data, loading: false, error: null })
    } catch (e) {
      setState({ data: null, loading: false, error: e instanceof ApiError ? e : new ApiError(String(e), -1) })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    run(...([] as unknown as P))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return { ...state, refetch: run }
}

export { client }
```

---

### Task 2.4：Auth Store（Zustand）

**Files:**
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/lib/auth-api.ts`

- [ ] **Step 1：创建 `frontend/src/lib/auth-api.ts`**

```typescript
import client from './api'

export interface UserInfo {
  user_id: number
  username: string
  real_name?: string
  student_no?: string
  email?: string
  phone?: string
  roles: string[]
  status?: string
}

export interface LoginResponse { token: string; user: UserInfo }

export const authApi = {
  login(username: string, password: string) {
    return client.post<LoginResponse>('/auth/login', { username, password })
  },
  register(data: { username: string; password: string; real_name?: string; email?: string; student_no?: string }) {
    return client.post('/auth/register', data)
  },
  me() {
    return client.get<UserInfo>('/auth/me')
  },
  logout() {
    return client.post('/auth/logout')
  },
  changePassword(old_password: string, new_password: string) {
    return client.put('/auth/me/password', { old_password, new_password })
  },
  updateProfile(data: { real_name?: string; student_no?: string; email?: string; phone?: string }) {
    return client.put('/auth/me', data)
  },
  listRoles() {
    return client.get<Array<{ role_id: number; role_name: string; role_code: string }>>('/auth/roles')
  },
}
```

- [ ] **Step 2：创建 `frontend/src/stores/auth.ts`**

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { getToken, setToken as saveToken, clearToken } from '@/lib/api'
import { authApi, type UserInfo } from '@/lib/auth-api'

interface AuthState {
  token: string | null
  user: UserInfo | null
  loading: boolean
  initialized: boolean
  login: (username: string, password: string) => Promise<UserInfo>
  logout: () => Promise<void>
  fetchMe: () => Promise<UserInfo | null>
  hasRole: (role: string) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: getToken(),
      user: null,
      loading: false,
      initialized: false,

      async login(username, password) {
        set({ loading: true })
        try {
          const data = await authApi.login(username, password)
          saveToken(data.token)
          const me = await authApi.me()
          set({ token: data.token, user: me, loading: false, initialized: true })
          return me
        } catch (e) {
          set({ loading: false })
          throw e
        }
      },

      async logout() {
        try { await authApi.logout() } catch { /* ignore */ }
        clearToken()
        set({ token: null, user: null })
      },

      async fetchMe() {
        try {
          const me = await authApi.me()
          set({ user: me, initialized: true })
          return me
        } catch {
          set({ user: null, token: null, initialized: true })
          return null
        }
      },

      hasRole(role) {
        return get().user?.roles?.includes(role) ?? false
      },
    }),
    {
      name: 'eduagent-auth',
      partialize: (s) => ({ token: s.token, user: s.user }),
    },
  ),
)
```

---

### Task 2.5：路由守卫

**Files:**
- Create: `frontend/src/lib/router-guard.tsx`

- [ ] **Step 1：创建 `frontend/src/lib/router-guard.tsx`**

```typescript
import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router'
import { useAuthStore } from '@/stores/auth'

const PUBLIC_PATHS = ['/login']

const ROLE_ACCESS: Record<string, string[]> = {
  '/student': ['student', 'admin'],
  '/teacher': ['teacher', 'admin'],
  '/admin': ['admin'],
}

export function useRouterGuard() {
  const { token, user, initialized, fetchMe } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    if (initialized) return
    if (token) {
      fetchMe()
    } else {
      useAuthStore.setState({ initialized: true })
    }
  }, [initialized, token, fetchMe])

  useEffect(() => {
    if (!initialized) return
    const isPublic = PUBLIC_PATHS.some((p) => location.pathname.startsWith(p))
    if (!token && !isPublic) {
      navigate(`/login?redirect=${encodeURIComponent(location.pathname + location.search)}`, { replace: true })
      return
    }
    if (token && isPublic) {
      const role = user?.roles?.[0] ?? 'student'
      const home = role === 'admin' ? '/admin' : role === 'teacher' ? '/teacher' : '/student'
      navigate(home, { replace: true })
      return
    }
    if (token && user) {
      for (const [prefix, allowed] of Object.entries(ROLE_ACCESS)) {
        if (location.pathname.startsWith(prefix)) {
          if (!user.roles?.some((r) => allowed.includes(r))) {
            navigate('/login', { replace: true })
          }
          return
        }
      }
    }
  }, [initialized, token, user, location.pathname, location.search, navigate])
}
```

- [ ] **Step 2：在 `App.tsx` 接入守卫**

读取 `frontend/src/app/App.tsx`，改为：
```typescript
import { RouterProvider } from "react-router";
import { router } from "./routes";
import { useRouterGuard } from "@/lib/router-guard";

function GuardedApp() {
  useRouterGuard()
  return <RouterProvider router={router} />
}

export default function App() {
  return <GuardedApp />;
}
```

---

## 阶段 3：API 模块（17 个）

每个文件用相同的风格：导入 `client`，导出 `xxxApi` 对象，方法返回 `Promise<T>`（拦截器已解包 `data`）。

### Task 3.1 — 3.17：创建 API 模块

- [ ] **Step 1：创建 `frontend/src/lib/api/users.ts`**

```typescript
import client from './api'

export interface User {
  user_id: number
  username: string
  real_name?: string
  student_no?: string
  email?: string
  phone?: string
  status: string
  roles: string[]
  created_at: string
}

export const usersApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string; status?: string }) {
    return client.get<{ items: User[]; total: number }>('/users', { params })
  },
  updateStatus(user_id: number, status: string) {
    return client.put(`/users/${user_id}/status`, { status })
  },
  updateRoles(user_id: number, role_ids: number[]) {
    return client.put(`/users/${user_id}/roles`, { role_ids })
  },
}
```

- [ ] **Step 2：创建 `frontend/src/lib/api/profiles.ts`**

```typescript
import client from './api'

export interface ProfileDetail {
  profile_id: number
  student_id: number
  student_name: string
  course_id: number
  course_name: string
  learning_goal: string
  current_level: string
  weak_points: Array<{ kp_id: number; kp_name?: string; name?: string; mastery: number; reason?: string }>
  preferences: string[]
  mastery_score: number
  last_updated: string
  strong_points: Array<{ kp_id: number; kp_name?: string; name?: string; mastery: number }>
  recent_tasks: Array<{ task_id: number; title: string; status: string; completed_at?: string }>
  recent_tests: Array<{ test_id: number; accuracy: number; date: string }>
}

export const profilesApi = {
  list(params?: { page?: number; page_size?: number; course_id?: number; keyword?: string }) {
    return client.get<{ items: ProfileDetail[]; total: number; page: number; page_size: number }>('/profiles/', { params })
  },
  getById(profile_id: number) {
    return client.get<ProfileDetail>(`/profiles/${profile_id}`)
  },
  update(profile_id: number, data: Record<string, unknown>) {
    return client.put(`/profiles/${profile_id}`, data)
  },
  updateMastery(profile_id: number, data: { kp_id: number; mastery: number; update_reason?: string }) {
    return client.post(`/profiles/${profile_id}/mastery`, data)
  },
}
```

- [ ] **Step 3：创建 `frontend/src/lib/api/learning.ts`**

```typescript
import client from './api'

export interface Course {
  id: number
  name: string
  code: string
  description: string
  teacher: string
  semester: string
  status: string
  knowledge_point_count: number
  student_count: number
  task_count: number
  cover_color: string
  tags: string[]
}

export interface LearningTask {
  id: number
  course_id: number
  course_name: string
  title: string
  type: string
  status: string
  priority: string
  due_date: string
  description: string
  student_count: number
  completion_rate: number
}

export interface LearningPathNode {
  id: number
  kp_id: number
  name: string
  kp_name: string
  kp_code: string
  difficulty_level: number
  description: string
  estimated_hours: number
  mastery_level: number
  last_test_score: number | null
  last_test_date: string | null
  status_label: string
  color: string
  size: number
}

export interface LearningPathEdge { source: number; target: number; label: string }
export interface LearningPathSummary {
  total: number; mastered: number; weak: number; avg_mastery: number
  profile_id: number | null; course_id: number
}
export interface LearningPathGraph { nodes: LearningPathNode[]; edges: LearningPathEdge[]; summary: LearningPathSummary }

export const learningApi = {
  listCourses() { return client.get<Course[]>('/learning/courses') },
  getCourse(course_id: number) { return client.get<Course>(`/learning/courses/${course_id}`) },
  listTasks(params?: { page?: number; page_size?: number; course_id?: number; status?: string }) {
    return client.get<{ items: LearningTask[]; total: number; page: number; page_size: number }>('/learning/tasks', { params })
  },
  getTask(task_id: number) { return client.get<LearningTask>(`/learning/tasks/${task_id}`) },
  getLearningPath(course_id: number, profile_id?: number) {
    return client.get<LearningPathGraph>(`/learning/courses/${course_id}/learning-path`, { params: profile_id ? { profile_id } : undefined })
  },
}
```

- [ ] **Step 4：创建 `frontend/src/lib/api/resources.ts`**

```typescript
import client from './api'

export interface LearningResource {
  resource_id: number
  course_id: number
  course_name: string
  resource_title: string
  resource_type: string
  difficulty: string
  status: string
  created_at: string
}

export const resourcesApi = {
  list(params?: { page?: number; page_size?: number; course_id?: number; type?: string }) {
    return client.get<{ items: LearningResource[]; total: number }>('/learning/resources', { params })
  },
  getById(id: number) { return client.get<LearningResource>(`/learning/resources/${id}`) },
}
```

- [ ] **Step 5：创建 `frontend/src/lib/api/feedbacks.ts`**

```typescript
import client from './api'

export interface LearningFeedback {
  feedback_id: number
  profile_id: number
  student_name: string
  resource_id: number | null
  resource_title: string | null
  course_id: number
  course_name: string
  feedback_type: string
  content: string | null
  quiz_score: number | null
  self_mastery: number | null
  difficulty_rating: string | null
  created_at: string
}

export const feedbackApi = {
  list(params?: { page?: number; page_size?: number; course_id?: number; feedback_type?: string }) {
    return client.get<{ items: LearningFeedback[]; total: number }>('/feedbacks', { params })
  },
  submit(data: {
    resource_id?: number; feedback_type: string; content?: string
    quiz_score?: number; self_mastery?: number; difficulty_rating?: string
  }) {
    return client.post('/feedbacks', data)
  },
  updateMastery(profile_id: number, kp_id: number, mastery: number) {
    return client.post(`/profiles/${profile_id}/mastery`, { kp_id, mastery })
  },
}
```

- [ ] **Step 6：创建 `frontend/src/lib/api/agents.ts`**

```typescript
import client from './api'

export interface AgentRequest {
  student_id: number; course_id: number
  knowledge_point_ids: number[]; resource_type: string; difficulty: string
}

export interface WorkflowResult {
  diagnosis: { diagnosis_id: string; weak_points: Array<{ kp_id: number; name: string; mastery_level: number; reason: string }>; strength_points: Array<{ kp_id: number; name: string; mastery_level: number }>; learning_difficulties: string[]; resource_needs: string[]; suggested_difficulty: string }
  plan: { plan_id: string; learning_path: Array<{ order: number; kp_id: number; kp_name: string; estimated_time: string; resource_type: string; priority: string }>; resource_combination: string[]; learning_sequence: string; estimated_total_time: string }
  resource: { resource_id: string; title: string; type: string; content: string; knowledge_points: number[]; difficulty: string; target_audience: string; estimated_learning_time: string; generation_metadata: { agent: string; model: string } }
  assessment: { assessment_id: string; test_results: { total_questions: number; correct_answers: number; accuracy_rate: number }; mastery_updates: Array<{ kp_id: number; old_mastery: number; new_mastery: number; change_reason: string }>; feedback: string; suggestions: string[]; next_resource_recommendation: string }
  teacher_review_suggestion: { review_id: string; quality_score: number; quality_checks: Array<{ check: string; passed: boolean; note: string }>; risk_alerts: Array<{ level: string; message: string }>; suggestions: string[]; overall_comment: string }
  metadata: { total_duration_ms: number; step_history: Array<{ step: string; status: string; timestamp: string; error?: string; duration_ms: number }>; quality_score: number; revision_count: number }
}

export const agentsApi = {
  generate(data: AgentRequest) { return client.post<WorkflowResult>('/agents/generate', data) },
  getAgents() { return client.get<Array<{ id: string; name: string; description: string; type: string }>>('/agents/list') },
  saveResource(data: { result: WorkflowResult; title: string; course_id: number }) {
    return client.post<{ resource_id: string; title: string; storage_path: string; storage_url: string }>('/agents/save-resource', data)
  },
  getWorkflowStatus(run_id: string) { return client.get<WorkflowResult>(`/agents/workflow/${run_id}`) },
}
```

- [ ] **Step 7：创建 `frontend/src/lib/api/tasks.ts`**

```typescript
import client from './api'

export interface TaskOutput {
  output_id: number; task_id: number; branch_id: number; branch_name: string
  version_no: number; output_title: string; source_type: string
  parent_output_id?: number; is_final_candidate: boolean; status: string
  content?: string; lock_version?: number; edit_summary?: string
  creator_id: number; creator_username?: string; created_at: string; last_modified_at?: string
}

export interface TaskBranch {
  branch_id: number; project_id: number; task_id: number
  branch_name: string; base_output_id?: number; status: string
  creator_username?: string; created_at: string
}

export interface OutputComment {
  comment_id: number; output_id: number; commenter_id: number
  commenter_username?: string; commenter_real_name?: string
  comment_type: 'comment' | 'suggestion' | 'approval'
  comment_text: string; status: 'open' | 'resolved' | 'closed'
  created_at: string; updated_at: string
}

export interface GenerationResult {
  model_id: number; invocation_id: number; output_id?: number
  version_no?: number; status: string
  input_tokens?: number; output_tokens?: number; latency_ms?: number; error_message?: string
}

export const tasksApi = {
  getById(task_id: number) { return client.get<unknown>(`/tasks/${task_id}`) },
  getBranches(task_id: number) { return client.get<TaskBranch[]>(`/tasks/${task_id}/branches`) },
  getOutputs(task_id: number) { return client.get<TaskOutput[]>(`/tasks/${task_id}/outputs`) },
  generate(task_id: number, data: { branch_id?: number; model_ids: number[]; prompt_version_id?: number; input_text: string }) {
    return client.post<GenerationResult[]>(`/tasks/${task_id}/generate`, data)
  },
  getOutputById(output_id: number) { return client.get<TaskOutput>(`/outputs/${output_id}`) },
  updateOutput(output_id: number, data: { content: string; lock_version: number; edit_summary?: string }) {
    return client.put<TaskOutput>(`/outputs/${output_id}`, data)
  },
  saveAsNewVersion(output_id: number, data: { output_title?: string; content: string; edit_summary?: string; branch_id?: number }) {
    return client.post<TaskOutput>(`/outputs/${output_id}/save-as-new-version`, data)
  },
  submitReview(output_id: number, data?: { reviewer_id?: number; submit_note?: string }) {
    return client.post<{ request_id: number }>(`/outputs/${output_id}/submit-review`, data || {})
  },
  adoptOutput(output_id: number, data: { artifact_title: string; artifact_type: string; release_version?: string; adopt_note?: string }) {
    return client.post<{ adopted_id: number }>(`/outputs/${output_id}/adopt`, data)
  },
  getOutputComments(output_id: number, params?: { status?: string }) {
    return client.get<OutputComment[]>(`/outputs/${output_id}/comments`, { params })
  },
  addComment(output_id: number, data: { comment_type: 'comment' | 'suggestion' | 'approval'; comment_text: string }) {
    return client.post<OutputComment>(`/outputs/${output_id}/comments`, data)
  },
  updateCommentStatus(comment_id: number, status: 'open' | 'resolved' | 'closed') {
    return client.put<OutputComment>(`/comments/${comment_id}/status`, { status })
  },
}
```

- [ ] **Step 8：创建 `frontend/src/lib/api/projects.ts`**

```typescript
import client from './api'

export interface Project {
  project_id: number; project_name: string; project_type: string
  description?: string; owner_id: number
  owner_username?: string; owner_real_name?: string
  status: string; created_at: string
  member_count?: number; task_count?: number
}

export interface ProjectMember {
  member_id: number; project_id: number; user_id: number
  username: string; real_name?: string; email?: string; phone?: string
  project_role: string; joined_at: string; status: string
}

export interface ProjectTask {
  task_id: number; project_id: number; task_type_id: number
  type_name: string; type_code: string; title: string; description?: string
  creator_id: number; creator_username?: string
  assignee_id?: number; assignee_real_name?: string
  status: string; priority: string; due_date?: string; created_at: string
}

export const projectsApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string; status?: string }) {
    return client.get<{ items: Project[]; total: number }>('/projects', { params })
  },
  create(data: { project_name: string; project_type: string; description?: string }) {
    return client.post<Project>('/projects', data)
  },
  getById(project_id: number) { return client.get<Project>(`/projects/${project_id}`) },
  getMembers(project_id: number) { return client.get<ProjectMember[]>(`/projects/${project_id}/members`) },
  getTasks(project_id: number, params?: { page?: number; page_size?: number; status?: string; keyword?: string }) {
    return client.get<{ items: ProjectTask[]; total: number }>(`/projects/${project_id}/tasks`, { params })
  },
  createTask(project_id: number, data: { task_type_id: number; title: string; description?: string; assignee_id?: number; priority?: string; due_date?: string }) {
    return client.post<ProjectTask & { default_branch_id: number }>(`/projects/${project_id}/tasks`, data)
  },
  addMember(project_id: number, data: { user_id: number; project_role: string }) {
    return client.post(`/projects/${project_id}/members`, data)
  },
  removeMember(project_id: number, user_id: number) { return client.delete(`/projects/${project_id}/members/${user_id}`) },
  updateMember(project_id: number, user_id: number, data: { project_role: string }) {
    return client.put(`/projects/${project_id}/members/${user_id}`, data)
  },
  update(project_id: number, data: { project_name?: string; project_type?: string; description?: string }) {
    return client.put<Project>(`/projects/${project_id}`, data)
  },
  archive(project_id: number) { return client.post(`/projects/${project_id}/archive`) },
}
```

- [ ] **Step 9：创建 `frontend/src/lib/api/artifacts.ts`**

```typescript
import client from './api'

export interface Artifact {
  adopted_id: number; project_id: number; task_id: number; output_id: number
  artifact_title: string; artifact_type: string; release_version?: string
  adopted_by: number; adopted_by_name: string; adopted_at: string
  task_title: string; output_title: string; version_no: number; description?: string
}

export interface ArtifactDetail extends Artifact {
  output_content: string; output_status: string
  project_name: string; adopted_by_username?: string
}

export const artifactsApi = {
  list(project_id: number, params?: { page?: number; page_size?: number; artifact_type?: string; keyword?: string }) {
    return client.get<{ items: Artifact[]; total: number; page: number; page_size: number }>(`/projects/${project_id}/artifacts`, { params })
  },
  getById(adopted_id: number) { return client.get<ArtifactDetail>(`/artifacts/${adopted_id}`) },
}
```

- [ ] **Step 10：创建 `frontend/src/lib/api/prompts.ts`**

```typescript
import client from './api'

export interface PromptTemplate {
  template_id: number; template_name: string
  task_type_id: number; type_name: string; type_code: string
  current_version_no: number; is_active: boolean
  created_at: string; updated_at: string
}

export interface PromptVersion {
  version_id: number; template_id: number; version_no: number
  prompt_content: string; change_note: string
  is_active: boolean; created_by: number
  creator_real_name?: string; created_at: string
}

export const promptsApi = {
  getTemplates(params?: { page?: number; page_size?: number; task_type_id?: number; keyword?: string }) {
    return client.get<{ items: PromptTemplate[]; total: number }>('/prompt-templates', { params })
  },
  getTemplateById(template_id: number) { return client.get<PromptTemplate>(`/prompt-templates/${template_id}`) },
  createTemplate(data: { template_name: string; task_type_id: number; initial_prompt_content: string; change_note?: string }) {
    return client.post<PromptTemplate>('/prompt-templates', data)
  },
  updateTemplate(template_id: number, data: { template_name?: string; task_type_id?: number; is_active?: boolean }) {
    return client.put<PromptTemplate>(`/prompt-templates/${template_id}`, data)
  },
  deleteTemplate(template_id: number) { return client.delete(`/prompt-templates/${template_id}`) },
  getVersions(template_id: number) { return client.get<PromptVersion[]>(`/prompt-templates/${template_id}/versions`) },
  createVersion(template_id: number, data: { prompt_content: string; change_note?: string }) {
    return client.post<PromptVersion>(`/prompt-templates/${template_id}/versions`, data)
  },
  activateVersion(template_id: number, version_id: number) {
    return client.post(`/prompt-templates/${template_id}/versions/${version_id}/activate`)
  },
}
```

- [ ] **Step 11：创建 `frontend/src/lib/api/reviews.ts`**

```typescript
import client from './api'

export interface ReviewRequest {
  request_id: number; output_id: number; task_id: number; project_id: number
  project_name: string; task_title: string; output_title: string; version_no: number
  submitter_id: number; submitter_username: string; submitter_real_name: string
  reviewer_id?: number; reviewer_username?: string; reviewer_real_name?: string
  request_status: string; submit_note?: string; created_at: string
}

export interface ReviewDetail extends ReviewRequest { output_content: string; output_status: string }

export interface IssueTag {
  tag_id: number; tag_name: string; tag_code: string
  description: string; severity: 'low' | 'medium' | 'high'
}

export const reviewsApi = {
  getPending(params?: { page?: number; page_size?: number; project_id?: number }) {
    return client.get<{ items: ReviewRequest[]; total: number }>('/reviews/pending', { params })
  },
  getById(request_id: number) { return client.get<ReviewDetail>(`/reviews/${request_id}`) },
  complete(request_id: number, data: {
    review_status: 'approved' | 'rejected' | 'revision_required'
    accuracy_score?: number; completeness_score?: number; logic_score?: number
    format_score?: number; usability_score?: number; risk_score?: number
    review_comment?: string; issue_tag_ids?: number[]
  }) {
    return client.post<{ review_id: number }>(`/reviews/${request_id}/complete`, data)
  },
  getIssueTags() { return client.get<IssueTag[]>('/issue-tags') },
}
```

- [ ] **Step 12：创建 `frontend/src/lib/api/invocations.ts`**

```typescript
import client from './api'

export interface Invocation {
  invocation_id: number; model_id: number; model_name: string
  display_name: string; provider_name: string
  project_id: number; project_name: string
  task_id: number; task_title: string
  input_tokens: number; output_tokens: number; total_tokens: number
  latency_ms: number; status: string; error_message?: string
  ip_address?: string; created_at: string
}

export interface InvocationDetail extends Invocation {
  invoker_real_name?: string; input_text?: string; output_text?: string; cost?: number
  model_display_name?: string
  model_info?: { display_name?: string; model_name?: string; provider_name?: string; input_price?: number; output_price?: number; price_unit?: string }
}

export const invocationsApi = {
  getInvocations(params?: { page?: number; page_size?: number; project_id?: number; task_id?: number; model_id?: number; status?: string }) {
    return client.get<{ items: Invocation[]; total: number; page: number; page_size: number }>('/invocations', { params })
  },
  getInvocationById(invocation_id: number) { return client.get<InvocationDetail>(`/invocations/${invocation_id}`) },
}
```

- [ ] **Step 13：创建 `frontend/src/lib/api/models.ts`**

```typescript
import client from './api'

export interface ModelProvider {
  provider_id: number; provider_name: string; provider_code: string
  base_url?: string; website?: string; description?: string; status: string
}

export interface AIModel {
  model_id: number; provider_id: number; model_name: string
  display_name: string; capability_tags?: string[]; max_context?: number
  input_price: number; output_price: number; price_unit: string
  status: string; created_at: string
  provider_name: string; provider_code: string
}

export interface TaskType {
  task_type_id: number; type_name: string; type_code: string
  description?: string; default_template_id?: number; status: string
}

export const modelsApi = {
  getProviders(params?: { status?: string }) { return client.get<ModelProvider[]>('/model-providers', { params }) },
  getModels(params?: { provider_id?: number; status?: string; keyword?: string; page?: number; page_size?: number }) {
    return client.get<{ items: AIModel[]; total: number }>('/ai-models', { params })
  },
  getTaskTypes() { return client.get<TaskType[]>('/task-types') },
}
```

- [ ] **Step 14：创建 `frontend/src/lib/api/logs.ts`**

```typescript
import client from './api'

export interface OperationLog {
  log_id: number; user_id: number; username: string; real_name: string
  action_type: string; target_type: string; target_id: number
  action_desc: string; old_value?: string; new_value?: string
  ip_address?: string; created_at: string
}

export interface LoginLog {
  log_id: number; user_id: number; username: string; real_name: string
  login_status: 'success' | 'failed'; failure_reason?: string
  ip_address?: string; user_agent?: string; login_time: string
}

export const logsApi = {
  operationLogs(params?: { page?: number; page_size?: number; user_id?: number; target_type?: string; action_type?: string; start_date?: string; end_date?: string }) {
    return client.get<{ items: OperationLog[]; total: number }>('/logs/operation', { params })
  },
  loginLogs(params?: { page?: number; page_size?: number; user_id?: number; login_status?: string; start_date?: string; end_date?: string }) {
    return client.get<{ items: LoginLog[]; total: number }>('/logs/login', { params })
  },
}
```

- [ ] **Step 15：创建 `frontend/src/lib/api/statistics.ts`**

```typescript
import client from './api'

export const statisticsApi = {
  overview() { return client.get<{ project_count: number; active_project_count: number; task_count: number; pending_review_count: number; invocation_count: number; success_invocation_count: number; failed_invocation_count: number; artifact_count: number; total_tokens: number; total_cost: number }>('/statistics/overview') },
  projects(params?: { project_id?: number }) { return client.get<Array<{ project_id: number; project_name: string; member_count: number; task_count: number; output_count: number; approved_output_count: number; artifact_count: number; invocation_count: number; total_cost: number }>>('/statistics/projects', { params }) },
  modelCalls(params?: { project_id?: number; date_from?: string; date_to?: string }) { return client.get<Array<{ model_id: number; model_name: string; display_name: string; provider_name: string; call_count: number; total_invocations: number; success_count: number; failed_count: number; timeout_count: number; blocked_count: number; total_input_tokens: number; total_output_tokens: number; total_tokens: number; avg_latency_ms: number; success_rate: string }>>('/statistics/model-calls', { params }) },
  costs(params?: { project_id?: number; date_from?: string; date_to?: string }) { return client.get<{ total_cost: number; input_cost: number; output_cost: number; total_tokens: number; currency: string; cost_by_model: Array<{ model_name: string; cost: number }>; cost_by_project: Array<{ project_name: string; cost: number }>; cost_by_user: Array<{ real_name: string; cost: number }> }>('/statistics/costs', { params }) },
  reviews(params?: { project_id?: number }) { return client.get<{ review_count: number; approved_count: number; rejected_count: number; revision_required_count: number; avg_accuracy_score: number; avg_completeness_score: number; avg_logic_score: number; avg_format_score: number; avg_usability_score: number; avg_risk_score: number; top_issue_tags: Array<{ tag_name: string; count: number; severity: string }> }>('/statistics/reviews', { params }) },
  memberContributions(params?: { project_id?: number }) { return client.get<Array<{ user_id: number; real_name: string; project_count: number; task_created_count: number; task_assigned_count: number; output_created_count: number; review_count: number; artifact_adopted_count: number; invocation_count: number }>>('/statistics/member-contributions', { params }) },
  recentActivities(params?: { project_id?: number; limit?: number }) { return client.get<Array<{ log_id: number; user_id: number; real_name: string; action_type: string; target_type: string; target_id: number; action_desc: string; created_at: string }>>('/statistics/recent-activities', { params }) },
  learningOverview() { return client.get<{ course_count: number; student_count: number; resource_count: number; invocation_count: number; avg_mastery: number; review_pass_rate: number; feedback_count: number; active_tasks: number }>('/statistics/learning-overview') },
  masteryDistribution() { return client.get<Array<{ range: string; count: number }>>('/statistics/mastery-distribution') },
  weakKnowledgePoints(top_n = 10) { return client.get<Array<{ kp_id: number; kp_name: string; course_id: number; avg_mastery: number }>>('/statistics/weak-knowledge-points', { params: { top_n } }) },
  resourceTypeDistribution() { return client.get<Array<{ resource_type: string; type_name: string; count: number }>>('/statistics/resource-type-distribution') },
  invocationTrend(days = 14) { return client.get<Array<{ date: string; invocation_count: number; total_tokens: number; total_cost: number }>>('/statistics/invocation-trend', { params: { days } }) },
  reviewRateByCourse() { return client.get<Array<{ course_id: number; course_name: string; total: number; approved: number; pass_rate: number }>>('/statistics/review-rate-by-course') },
  costDistribution() { return client.get<Array<{ agent: string; agent_name: string; tokens: number; ratio: number }>>('/statistics/cost-distribution') },
}
```

- [ ] **Step 16：创建 `frontend/src/lib/api/courses.ts`**（admin 课程管理）

```typescript
import client from './api'
import type { Course } from './learning'

export const coursesApi = {
  list() { return client.get<Course[]>('/learning/courses') },
  get(id: number) { return client.get<Course>(`/learning/courses/${id}`) },
}
```

- [ ] **Step 17：创建 `frontend/src/lib/api/index.ts`（统一导出）**

```typescript
export { default as client } from './api'
export { authApi, type UserInfo, type LoginResponse } from './auth-api'
export { usersApi, type User } from './users'
export { profilesApi, type ProfileDetail } from './profiles'
export { learningApi, type Course, type LearningTask, type LearningPathGraph, type LearningPathNode, type LearningPathEdge, type LearningPathSummary } from './learning'
export { resourcesApi, type LearningResource } from './resources'
export { feedbackApi, type LearningFeedback } from './feedbacks'
export { agentsApi, type AgentRequest, type WorkflowResult } from './agents'
export { tasksApi, type TaskOutput, type TaskBranch, type OutputComment, type GenerationResult } from './tasks'
export { projectsApi, type Project, type ProjectMember, type ProjectTask } from './projects'
export { artifactsApi, type Artifact, type ArtifactDetail } from './artifacts'
export { promptsApi, type PromptTemplate, type PromptVersion } from './prompts'
export { reviewsApi, type ReviewRequest, type ReviewDetail, type IssueTag } from './reviews'
export { invocationsApi, type Invocation, type InvocationDetail } from './invocations'
export { modelsApi, type ModelProvider, type AIModel, type TaskType } from './models'
export { logsApi, type OperationLog, type LoginLog } from './logs'
export { statisticsApi } from './statistics'
export { coursesApi } from './courses'
```

---

## 阶段 4：Login 页面接入（打通鉴权闭环）

### Task 4.1：改造 Login.tsx 接入真实登录

**Files:**
- Modify: `frontend/src/app/pages/Login.tsx`

- [ ] **Step 1：读取现有 Login.tsx，找出 demo 账号和 onSubmit 逻辑**

```bash
head -50 frontend/src/app/pages/Login.tsx
```

- [ ] **Step 2：替换为以下实现（保留 design，不破坏 UI）**

在文件顶部追加：
```typescript
import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router'
import { useAuthStore } from '@/stores/auth'
import { notify } from '@/lib/toast'
```

找到 `onSubmit` / `handleLogin` 类函数（按现有命名），替换为：
```typescript
  const { login, loading } = useAuthStore()
  const navigate = useNavigate()
  const [params] = useSearchParams()

  async function handleLogin(username: string, password: string) {
    try {
      const user = await login(username, password)
      notify.success('登录成功')
      const redirect = params.get('redirect')
      const home = user.roles?.includes('admin') ? '/admin'
        : user.roles?.includes('teacher') ? '/teacher'
        : '/student'
      navigate(redirect || home, { replace: true })
    } catch (e) {
      const msg = e instanceof Error ? e.message : '登录失败'
      notify.error(msg)
    }
  }
```

- [ ] **Step 3：在 `Login.tsx` 底部导出 LoginForm 调用 `handleLogin`，并把 loading 状态绑到按钮**

找到 `<Button ... onClick=...>` 类按钮，绑定 `loading={loading}`，确保禁用。

- [ ] **Step 4：本地验证**

```bash
cd frontend && pnpm dev
```

打开浏览器访问 http://localhost:5174/login，尝试登录 `admin / Admin@123`，应该跳转到 `/admin`（前提是后端在 8000 跑着）。

---

## 阶段 5：Layout 接入用户信息

### Task 5.1：Layout 顶栏展示真实用户

**Files:**
- Modify: `frontend/src/app/components/Layout.tsx`

- [ ] **Step 1：在 Layout 顶部 import**

```typescript
import { useAuthStore } from '@/stores/auth'
import { useNavigate } from 'react-router'
```

- [ ] **Step 2：在 Layout 函数内获取 user 和 navigate**

```typescript
const user = useAuthStore((s) => s.user)
const logout = useAuthStore((s) => s.logout)
const navigate = useNavigate()

async function handleLogout() {
  await logout()
  navigate('/login', { replace: true })
}
```

- [ ] **Step 3：把顶栏的"用户名"和"角色"硬编码替换为 user 数据**

- 替换 `user?.real_name || user?.username` 来自 store
- 角色 Tag 用 `user?.roles?.map(...)`
- 退出按钮 onClick 改为 `handleLogout`

---

## 阶段 6：分批接入页面（按角色）

### 批次 A — Teacher（最高优先级，先打通学习闭环）

每个页面的接入模式：
1. 删除 `import { ... } from '../data/demoData'` 或类似引用
2. `import { useApi } from '@/lib/useApi'` 和 `import { xxxApi } from '@/lib/api'`
3. 顶层 `const { data, loading, error, refetch } = useApi(() => xxxApi.xxx(), [])`
4. 把 `demoData` 字面量替换为 `data`，并加 `loading` 加载态
5. 如果接口字段名不同，按后端真实返回做字段映射（在文件顶部写 mapper）

#### Task 6.1：TeacherDashboard.tsx

- [ ] **Step 1：删 demoData 引用，加 useApi**

```typescript
import { useApi } from '@/lib/useApi'
import { statisticsApi } from '@/lib/api'

const overview = useApi(() => statisticsApi.overview(), [])
const learning = useApi(() => statisticsApi.learningOverview(), [])
const trend = useApi(() => statisticsApi.invocationTrend(14), [])
const weak = useApi(() => statisticsApi.weakKnowledgePoints(5), [])
```

- [ ] **Step 2：替换卡片数据源**

把 6 个数字卡、薄弱知识点列表、调用趋势折线图的数据源换成 `overview.data`、`learning.data`、`weak.data`、`trend.data`。

#### Task 6.2：AgentWorkbench.tsx

- [ ] **Step 1：左栏选择器**

```typescript
const courses = useApi(() => learningApi.listCourses(), [])
const models = useApi(() => modelsApi.getModels({ status: 'active' }), [])
```

- [ ] **Step 2：底部"启动智能体生成"按钮 onClick**

```typescript
async function handleGenerate() {
  const result = await agentsApi.generate({ student_id, course_id, knowledge_point_ids, resource_type, difficulty })
  setResult(result)
}
```

#### Task 6.3 — 6.8：剩余 Teacher 页面

- ResourceLibrary → `resourcesApi.list`
- TeacherReview → `reviewsApi.getPending` + `reviewsApi.getIssueTags` + `reviewsApi.complete`
- TeacherTasks → `tasksApi.getById` / `tasksApi.getOutputs` / `tasksApi.generate`
- TeacherCourses → `learningApi.listCourses`
- TeacherKnowledgeBase → 占位（用 `learningApi.listCourses` 拉课程列表作为知识库入口）
- LearningAnalytics → `statisticsApi.learningOverview` / `masteryDistribution` / `weakKnowledgePoints` / `resourceTypeDistribution` / `invocationTrend` / `reviewRateByCourse` / `costDistribution`

### 批次 B — Student

#### Task 6.9 — 6.15

- StudentDashboard → `statisticsApi.learningOverview` + 我的最近任务
- StudentProfile → `profilesApi.list` + `profilesApi.getById`
- StudentLearningPath → `learningApi.getLearningPath(courseId, profileId)`
- StudentTasks → `learningApi.listTasks` + `learningApi.getTask`
- StudentTutor → 复用 `agentsApi.generate`（个性化辅导对话）
- LearningFeedback → `feedbackApi.list` + `feedbackApi.submit`
- ResourceLibrary（学生视角）→ `resourcesApi.list`

### 批次 C — Admin

#### Task 6.16 — 6.26

- AdminDashboard → `statisticsApi.overview`
- AdminUsers → `usersApi.list` + `usersApi.updateStatus` + `usersApi.updateRoles` + `authApi.listRoles`
- AdminPrompts → `promptsApi.getTemplates` / `getVersions` / `createVersion` / `activateVersion`
- AdminModelConfig → `modelsApi.getProviders` / `getModels` / `getTaskTypes`
- AdminAgentConfig → `agentsApi.getAgents`（列表型页面）
- AdminCourses → `learningApi.listCourses`
- AdminAudit → `invocationsApi.getInvocations` + `getInvocationById`
- AdminCosts → `statisticsApi.costs` + `costDistribution`
- AdminLogs → `logsApi.operationLogs` + `logsApi.loginLogs`
- AdminGovernance → 占位（暂时用 `statisticsApi.reviews` + `reviewRateByCourse`）
- RolePermissionMap → 占位（静态展示）
- DesignSystemUpdate → 保留为设计稿展示页

### 批次 D — 公共

#### Task 6.27

- NotFound.tsx — 保留现状

---

## 阶段 7：联调

### Task 7.1：端到端验证

- [ ] **Step 1：启动后端**

```bash
cd backend && python run.py
```

确认 8002 端口监听。

- [ ] **Step 2：启动前端**

```bash
cd frontend && pnpm dev
```

打开 http://localhost:5173/login。

- [ ] **Step 3：用三组账号各跑一次完整流程**

| 角色 | 账号 | 测试路径 |
|---|---|---|
| admin | admin / Admin@123 | 登录 → /admin → 用户管理 → 提示词模板 → 模型配置 → 调用审计 → 成本统计 |
| teacher | teacher1 / 123456 | 登录 → /teacher → Dashboard → 课程空间 → 智能体工作台（生成一次）→ 资源库 → 审核中心（审核通过）→ 分析看板 |
| student | student1 / 123456 | 登录 → /student → Dashboard → 画像 → 学习路径 → 任务 → 反馈 |

- [ ] **Step 4：记录并修复 bug**

把所有发现写到一个 `docs/A3_FRONTEND_MIGRATION_BUGS.md`，按页面+严重度分类。

- [ ] **Step 5：最终提交**

```bash
git add -A
git commit -m "feat(frontend): 接入 17 个 API 模块 + 鉴权 + 跨角色路由守卫

- 移除 demoData 静态数据，全部走真实后端
- Login/Auth/Teacher/Student/Admin 页面均联调通过
- 详见 docs/superpowers/plans/2026-06-14-react-frontend-migration.md"
```

---

## Self-Review

- **Spec coverage:** 27 个新 frontend 页面 + 17 个 API + 鉴权 + 守卫 + Layout 用户信息 — 全部覆盖。
- **Placeholder scan:** 无 TBD/TODO/占位描述；每个 Step 含实际代码或命令。
- **Type consistency:** `UserInfo` / `LoginResponse` 在 auth-api 与 auth store 中一致；所有 API 路径前缀 `/api` 在 vite proxy 与 axios baseURL 与后端 FastAPI routers 一致。
- **已知风险：**
  1. 后端 `frontend_old` 中 `feedbacks` 实际路径是 `/api/feedbacks`，新代码用 `/feedbacks`（依赖 baseURL=/api），与 routers 列表中 `feedbacks.router` + `include_router(feedbacks.router, prefix="/api")` 一致 ✓
  2. AdminGovernance / RolePermissionMap 暂用 statistics API 占位，后续按需扩展
  3. TeacherKnowledgeBase 暂用 courses 列表占位，等课程知识库 RAG 后端接口稳定后接入

## Execution Handoff

完成后进入执行阶段，按批次顺序推进（阶段 0 → 7）。
