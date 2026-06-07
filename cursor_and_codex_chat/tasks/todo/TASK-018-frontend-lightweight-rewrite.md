# TASK-018: Frontend Lightweight Rewrite

## Basic Info

- **Task ID**: TASK-018-frontend-lightweight-rewrite
- **Stage**: 018
- **Role**: Cursor Frontend Engineer
- **Status**: Pending
- **Created**: 2026-06-02
- **Target**: Rewrite the frontend as a lightweight Vue3 demo, replacing the current V3 Admin Vite template frontend.

---

## Background & Motivation

The current V3 Admin Vite template frontend has persistent issues with:

- Port, proxy, CORS, and template residual configuration problems
- Complex login chain that breaks during local development
- Over-engineered dynamic routing, Mock system, and state management

The decision was made to abandon the template approach and rewrite a clean, lightweight Vue3 frontend for stable course demonstrations.

---

## Allowed Modifications

- `frontend/*`
- `cursor_and_codex_chat/handoff/HANDOFF-018-frontend-lightweight-rewrite.md`
- `frontend/README.md`

## Forbidden Modifications

- `backend/*`
- `database/*`
- `docs/01_数据库Schema冻结说明.md`

---

## Technical Stack

1. **Vue 3** (Composition API)
2. **Vite** (build tool, dev server with proxy)
3. **Element Plus** (UI component library)
4. **Axios** (HTTP client, with unified response interceptor)
5. **Pinia** (lightweight state management)
6. **Vue Router** (static routes, no dynamic loading)

---

## Must Implement

### Core Pages

1. [ ] Login page (`/login`)
2. [ ] Fetch current user after login (`GET /api/auth/me`)
3. [ ] Base backend layout (sidebar + header + content)
4. [ ] Top bar with user info display
5. [ ] Left sidebar navigation menu
6. [ ] Route guard (redirect to `/login` if unauthenticated)
7. [ ] Dashboard home page (`/`)
8. [ ] Project list page (`/projects`)
9. [ ] Project detail page (`/projects/:id`)
10. [ ] Task detail page (`/tasks/:id`)
11. [ ] AI generation basic panel
12. [ ] Output version viewer
13. [ ] Review center basic page (`/reviews`)
14. [ ] Artifact library basic page (`/artifacts`)
15. [ ] Statistics dashboard basic page (`/statistics`)

### Architecture

- [ ] Clean up old template complex structures
- [ ] Vite proxy routes all `/api/...` requests to backend
- [ ] Unified Axios response interceptor (code=0 success, code!=0 show message)
- [ ] Pinia store for auth (token, user info)
- [ ] Static route definitions, no dynamic routing
- [ ] `frontend/.env.development` with proxy config
- [ ] Updated `frontend/README.md`

---

## API Requirements

All requests go through `/api/...`. Proxy target: `http://127.0.0.1:8002`.

### Endpoints

| # | Method | Path | Description |
|---|--------|------|-------------|
| 1 | POST | `/api/auth/login` | Login |
| 2 | GET | `/api/auth/me` | Get current user |
| 3 | POST | `/api/auth/logout` | Logout |
| 4 | GET | `/api/projects` | Project list |
| 5 | GET | `/api/projects/{project_id}` | Project detail |
| 6 | GET | `/api/projects/{project_id}/tasks` | Project tasks |
| 7 | GET | `/api/tasks/{task_id}` | Task detail |
| 8 | GET | `/api/tasks/{task_id}/branches` | Branch list |
| 9 | GET | `/api/tasks/{task_id}/outputs` | Output list |
| 10 | GET | `/api/outputs/{output_id}` | Output detail |
| 11 | POST | `/api/tasks/{task_id}/generate` | AI generate |
| 12 | GET | `/api/reviews/pending` | Pending reviews |
| 13 | GET | `/api/projects/{project_id}/artifacts` | Artifact list |
| 14 | GET | `/api/statistics/overview` | Statistics overview |

### Response Format

Backend success:
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

Frontend Axios must:
- Treat `code === 0` as success
- Show `message` when `code !== 0`

---

## Prohibited

1. Do NOT re引入 V3 Admin Vite 模板
2. Do NOT use Apifox Mock
3. Do NOT call `/api/auth/register`
4. Do NOT hardcode real tokens
5. Do NOT hardcode real API Keys
6. Do NOT modify backend
7. Do NOT modify database
8. Do NOT implement complex permission system
9. Do NOT over-abstract
10. Do NOT keep old template residual files causing conflicts

---

## Deliverables

1. Clean `frontend/` directory — remove old template irrelevant files
2. A clear, runnable, lightweight Vue3 project
3. `frontend/.env.development` with proxy configuration
4. Updated `frontend/README.md`
5. Handoff document at:
   `cursor_and_codex_chat/handoff/HANDOFF-018-frontend-lightweight-rewrite.md`

### Handoff Must Include

1. Why switching from template to lightweight rewrite
2. Which files were modified
3. How to start frontend
4. How to start backend
5. How proxy is configured
6. Login test account
7. Implemented pages
8. Simplified or unimplemented content
9. Whether `npm install` / `npm run build` was executed
10. If cannot execute, state reason

---

## Execution Notes

### Backend

The backend is already running on `http://127.0.0.1:8000` from previous session.

### Backend needs to be started on port 8002

The frontend proxy targets `http://127.0.0.1:8002`, so the backend may need to be started on that port.

Check `backend/run.py` for port configuration, or start backend with:
```
cd backend
.venv\Scripts\Activate.ps1
python run.py --port 8002
```

### Verification Steps

After frontend rewrite is complete, verify:
1. `npm install` succeeds in `frontend/`
2. `npm run dev` starts without errors
3. Login page renders at `http://localhost:5173/login`
4. Login with test account succeeds
5. All 15 pages render without crash
6. No CORS errors (proxy is used)
7. No 404 on any implemented API call
