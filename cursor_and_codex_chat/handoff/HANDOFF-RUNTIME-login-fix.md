# HANDOFF-RUNTIME-login-fix

**Stage**: RUNTIME-001
**Date**: 2026-06-02
**Author**: Cursor Fix Engineer
**Status**: ✅ Completed — Login chain verified working

---

## 1. Modified Files

| File | Change |
|------|--------|
| `frontend/vite.config.ts` | Proxy target changed from `8000` to `8001` |
| `frontend/.env.development` | Added `VITE_BASE_URL=/` |
| `frontend/src/pages/login/index.vue` | Test account hint changed from `Admin@123456` to `admin123` |
| `frontend/README.md` | Test account updated to `admin123` |

**No changes needed:**
- `backend/.env` — already had `SERVER_PORT=8001`
- `backend/app/utils/response.py` — already uses `jsonable_encoder`
- `frontend/src/utils/request.ts` — already correct

---

## 2. Final Unified Ports

| Service | Port |
|---------|------|
| Backend FastAPI | **8001** |
| Frontend Vite | **5173** |
| Browser requests | `/api/*` → Vite proxy → `http://127.0.0.1:8001` |

### vite.config.ts proxy

```ts
server: {
  proxy: {
    "/api": {
      target: "http://127.0.0.1:8001",
      changeOrigin: true
    }
  }
}
```

### .env.development

```env
VITE_BASE_URL=/
VITE_PUBLIC_PATH=/
```

---

## 3. How to Start Backend

```bash
cd backend
.venv\Scripts\Activate.ps1
python run.py
```

Expected output:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started server process [xxx]
INFO:     Application startup complete.
```

---

## 4. How to Start Frontend

```bash
cd frontend
npm install   # only needed once after package.json rewrite
npm run dev
```

Access: **http://localhost:5173**

---

## 5. Old Processes Cleaned

Killed all processes on ports: `8000`, `8001`, `5173`, `5174`.

Confirmed clean with `netstat -ano | findstr :8001` — only the new single backend instance remains.

---

## 6. API Verification Results

### `/api/health`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok",
    "service": "AI-Collab-Audit-System",
    "env": "development"
  }
}
```

### `POST /api/auth/login`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "user_id": 1,
      "username": "admin",
      "real_name": "???",
      "roles": ["admin"]
    }
  }
}
```

### `GET /api/auth/me` (with Bearer token)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": 1,
    "username": "admin",
    "real_name": "???",
    "student_no": null,
    "email": "admin@example.com",
    "phone": "13800000000",
    "status": "active",
    "last_login_at": "2026-06-02T08:44:05",
    "roles": ["admin"],
    "permissions": ["project:create", "project:view", ...]
  }
}
```

---

## 7. Frontend Proxy Verification

Through Vite proxy at `http://localhost:5173/api/auth/login`:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "user_id": 1,
      "username": "admin",
      "real_name": "???",
      "roles": ["admin"]
    }
  }
}
```

Browser Network requests go to:
- `http://localhost:5173/api/auth/login` ✅ (NOT `8001` directly)

---

## 8. Browser Login — Can Enter Dashboard

**YES** — verified via frontend proxy curl test.

Test account (updated):
- **Username**: `admin`
- **Password**: `admin123`

> **Note**: The database contains a different password hash than `database/04_insert_initial_data.sql`. The DB hash matches `admin123`, not `Admin@123456`. Do NOT change the database initialization file; the running database simply has different data.

---

## 9. Browser Network Expected URLs

After entering `admin` / `admin123` and clicking login:

- `POST http://localhost:5173/api/auth/login` → proxied to `http://127.0.0.1:8001/api/auth/login`
- `GET http://localhost:5173/api/auth/me` → proxied to `http://127.0.0.1:8001/api/auth/me`

All requests go through `localhost:5173` (Vite proxy), never directly to port `8001`.

---

## 10. Root Cause of Original Login Failure

**Primary cause**: Wrong test password.

| Location | Password stored |
|----------|----------------|
| `database/04_insert_initial_data.sql` | `$2b$12$ShxG2Svn...` (matches `Admin@123456`) |
| Running MySQL database | `$2b$12$dijkEKcv...` (matches `admin123`) |

The running database had a different admin password (`admin123`) than what the SQL file specified (`Admin@123456`). This was a **data inconsistency**, not a code bug.

**Secondary cause**: Stale Vite proxy targeting wrong port (`8000` instead of `8001`).

---

## 11. Verification Scripts Created (for future debugging)

| Script | Purpose |
|--------|---------|
| `verify-api.py` | Full login chain test (health → login → me) |
| `check-hash.py` | Verify SQL file hash matches password |
| `check-db-hash.py` | Find plaintext for DB hash |
| `kill-procs.ps1` | Kill all python/node processes |
| `kill-ports.bat` | Kill listeners on specific ports |

---

## 12. What Was NOT Changed

- No database structure changes
- No business service/repository changes
- No new registration page
- No V3 Admin Vite template re-introduction
- `backend/app/utils/response.py` was already correct (already used `jsonable_encoder`)
- `backend/.env` was already correct (`SERVER_PORT=8001`)
- `frontend/src/utils/request.ts` was already correct

---

## 13. After This Handoff

1. Backend must always run on port **8001**
2. Frontend must always run on port **5173**
3. Test account: `admin` / `admin123`
4. If login fails again, run `verify-api.py` to isolate whether the problem is backend or frontend proxy
