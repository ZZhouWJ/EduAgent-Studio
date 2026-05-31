#!/usr/bin/env bash
# ============================================================
# AI-Collab-Audit-System - Backend API curl Examples
# ============================================================

BASE_URL="http://127.0.0.1:8000"
TOKEN="<YOUR_TOKEN>"
PROJECT_ID=1
TASK_ID=1
OUTPUT_ID=1
REQUEST_ID=1

# ============================================================
# 1. Health Checks
# ============================================================

# Service health check (no auth required)
curl -s -X GET "$BASE_URL/api/health"

# Database health check (no auth required)
curl -s -X GET "$BASE_URL/api/health/db"

# ============================================================
# 2. Auth
# ============================================================

# Login
curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<PLACEHOLDER_PASSWORD>"}'

# Get current user info
curl -s -X GET "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# ============================================================
# 3. Projects
# ============================================================

# List projects
curl -s -X GET "$BASE_URL/api/projects" \
  -H "Authorization: Bearer $TOKEN"

# Create project
curl -s -X POST "$BASE_URL/api/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "My Project",
    "description": "Project description",
    "project_type": "course_project",
    "course_name": "Software Engineering"
  }'

# ============================================================
# 4. Tasks
# ============================================================

# List project tasks
curl -s -X GET "$BASE_URL/api/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $TOKEN"

# Generate task outputs (AI generation)
curl -s -X POST "$BASE_URL/api/tasks/$TASK_ID/generate" \
  -H "Authorization: Bearer $TOKEN"

# ============================================================
# 5. Outputs (Reviews)
# ============================================================

# Submit output for review
curl -s -X POST "$BASE_URL/api/outputs/$OUTPUT_ID/submit-review" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"submit_note": "Please review this output"}'

# ============================================================
# 6. Reviews
# ============================================================

# Complete review
curl -s -X POST "$BASE_URL/api/reviews/$REQUEST_ID/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "review_status": "approved",
    "accuracy_score": 90,
    "completeness_score": 90,
    "logic_score": 90,
    "format_score": 90,
    "usability_score": 90,
    "risk_score": 5,
    "review_comment": "Good"
  }'

# ============================================================
# 7. Artifacts
# ============================================================

# Adopt output as artifact
curl -s -X POST "$BASE_URL/api/outputs/$OUTPUT_ID/adopt" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "artifact_title": "Final Report",
    "artifact_type": "document",
    "release_version": "v1.0",
    "adopt_note": "Adopted as final deliverable"
  }'

# ============================================================
# 8. Statistics
# ============================================================

# Overview statistics
curl -s -X GET "$BASE_URL/api/statistics/overview" \
  -H "Authorization: Bearer $TOKEN"

# Project statistics
curl -s -X GET "$BASE_URL/api/statistics/projects" \
  -H "Authorization: Bearer $TOKEN"
