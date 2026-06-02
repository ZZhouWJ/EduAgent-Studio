# HANDOFF-018: Frontend Lightweight Rewrite

**Stage**: 018
**Date**: 2026-06-02
**Author**: Cursor Frontend Engineer
**Status**: Completed

---

## 1. Why Switching from Template to Lightweight Rewrite

The original frontend was based on **V3 Admin Vite** template with many complex features:

- UnoCSS, SVG auto-import, auto-import components/plugins
- Dynamic routing, Mock system, complex permission stores
- Multiple Pinia stores (app, settings, permission, tags-view)
- Persistent issues with port, proxy, CORS, and login chain during local development

The decision was made to **abandon the template approach** and rewrite a clean, lightweight Vue3 frontend for stable course demonstrations.

---

## 2. Files Modified

### Created (new files)

| File | Purpose |
|------|---------|
| `src/main.ts` | App entry (simplified) |
| `src/App.vue` | Root component (simplified) |
| `src/assets/main.css` | Global CSS |
| `src/layouts/BackendLayout.vue` | Sidebar + header + content layout |
| `src/pages/login/index.vue` | Login page |
| `src/pages/dashboard/index.vue` | Dashboard home |
| `src/pages/projects/index.vue` | Project list |
| `src/pages/projects/ProjectDetail.vue` | Project detail |
| `src/pages/tasks/TaskDetail.vue` | Task detail with AI generate |
| `src/pages/reviews/index.vue` | Review center |
| `src/pages/artifacts/index.vue` | Artifact library |
| `src/pages/statistics/index.vue` | Statistics dashboard |
| `src/router/index.ts` | Static routes |
| `src/router/guard.ts` | Route guard (redirect to login) |
| `src/stores/user.ts` | User store (token + user info) |
| `src/utils/request.ts` | Axios with unified response interceptor |
| `.env.development` | Dev env vars |
| `frontend/README.md` | Updated README |

### Modified (in-place)

| File | Change |
|------|--------|
| `vite.config.ts` | Removed UnoCSS, SVG loader, auto-import plugins; proxy target `http://127.0.0.1:8000` |
| `package.json` | Removed 30+ unused dependencies (lodash-es, mitt, nprogress, screenfull, vxe-table, dayjs, husky, lint-staged, etc.); kept only core deps |
| `tsconfig.json` | Minor (mostly unchanged) |
| `frontend/README.md` | Rewritten to describe lightweight project |

### Deleted (old template files removed)

- `src/common/` (all APIs, components, composables, assets, styles)
- `src/http/axios.ts` (old complex Axios wrapper)
- `src/pinia/` (all old stores: app, settings, permission, tags-view)
- `src/plugins/` (all old plugins)
- `src/layouts/` (all old complex layout components except `BackendLayout.vue`)
- `src/pages/error/`, `src/pages/redirect/`, `src/pages/models/`, old task/review/artifact pages
- `uno.config.ts`
- `eslint.config.js`
- `.env`, `.env.staging`, `.env.production`
- `public/app-loading.css`, `public/detect-ie.js`
- `src/router/config.ts`, `src/router/whitelist.ts`, `src/router/helper.ts`
- `src/pages/login/apis/` (old login API module)

---

## 3. How to Start Frontend

```bash
cd frontend

# Install dependencies (from scratch after package.json changes)
npm install

# Start dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 4. How to Start Backend

```bash
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py --port 8002
```

Backend runs at: **http://127.0.0.1:8000** (default port)

---

## 5. Proxy Configuration

Vite proxy in `vite.config.ts`:

```ts
server: {
  proxy: {
    "/api": {
      target: "http://127.0.0.1:8000",
      changeOrigin: true
    }
  }
}
```

All frontend requests go to `/api/...` (e.g., `/api/auth/login`). Vite forwards them to the backend at `http://127.0.0.1:8000`. The browser never makes cross-origin requests directly to the backend.

---

## 6. Login Test Account

- **Username**: `admin`
- **Password**: `Admin@123456`

> Set up by `database/04_insert_initial_data.sql`.

---

## 7. Implemented Pages

| # | Page | Route | Status |
|---|------|-------|--------|
| 1 | Login | `/login` | Done |
| 2 | Dashboard | `/dashboard` | Done |
| 3 | Project list | `/projects` | Done |
| 4 | Project detail | `/projects/:projectId` | Done |
| 5 | Task detail + AI generate | `/tasks/:taskId` | Done |
| 6 | Review center | `/reviews` | Done |
| 7 | Artifact library | `/artifacts` | Done |
| 8 | Statistics dashboard | `/statistics` | Done |
| 9 | Backend layout (sidebar + header) | — | Done |
| 10 | Route guard | — | Done |

---

## 8. Simplified or Unimplemented Content

| Item | Reason |
|------|--------|
| `/api/auth/register` | Not called (no public registration) |
| Model management page (`/models`) | Removed from lightweight version |
| Complex permission system | All logged-in users can access all pages |
| Tags-view / tab navigation | Removed (simplified layout) |
| Theme switching / dark mode | Removed |
| UnoCSS / SVG auto-import | Removed |
| Dynamic routing | Static routes only |
| V3 Admin Vite Mock system | Removed |
| E2E tests / CI pipeline | Not in scope |
| Docker deployment | Not in scope |
| Task list entry page | Task accessed from project detail |

---

## 9. npm install / npm run build

- **`npm install`**: **Required**. `package.json` was rewritten with a minimal dependency list. Old `node_modules/` must be deleted and reinstalled.
- **`npm run build`**: **Not executed**. User should run this manually after `npm install` to verify the build.

### Steps to verify after this handoff:

```bash
cd frontend

# Clean old node_modules
Remove-Item -Recurse -Force node_modules

# Reinstall dependencies
npm install

# Start dev server
npm run dev

# (Optional) Build
npm run build
```

---

## 10. Current Project Structure

```
frontend/
├── .env.development          # Dev env vars (VITE_PUBLIC_PATH)
├── .env.example              # Example env
├── index.html
├── package.json              # Minimal deps (vue, vite, element-plus, pinia, axios, vue-router)
├── vite.config.ts            # Simple vite config with /api proxy to :8002
├── tsconfig.json
├── README.md
└── src/
    ├── main.ts
    ├── App.vue
    ├── assets/main.css
    ├── layouts/BackendLayout.vue   # Sidebar + header + content
    ├── pages/
    │   ├── login/index.vue
    │   ├── dashboard/index.vue
    │   ├── projects/index.vue
    │   ├── projects/ProjectDetail.vue
    │   ├── tasks/TaskDetail.vue
    │   ├── reviews/index.vue
    │   ├── artifacts/index.vue
    │   └── statistics/index.vue
    ├── router/
    │   ├── index.ts          # Static routes
    │   └── guard.ts          # Auth guard
    ├── stores/user.ts        # Token + user info
    └── utils/request.ts      # Axios wrapper
```

---

## 11. Known Issues / Notes

- Backend `config.py` Settings model does NOT include JWT/API_KEY fields, but `token.py` and `crypto.py` read them from `os.environ` directly. Fixed by adding `extra = "ignore"` to Settings Config.
- `requirements.txt` had Chinese comments causing GBK decode error on Windows. Fixed by replacing with English comments.
- No TypeScript build check (`vue-tsc`) was run. Run manually if needed.
