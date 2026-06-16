"""Comprehensive API endpoint test script."""
import requests
import json
from collections import defaultdict

BASE = "http://localhost:8000"

# Get auth token
resp = requests.post(f"{BASE}/api/auth/login", json={"username": "apitest", "password": "Test@123456"}, timeout=10)
token = resp.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}
print("Token obtained successfully\n")

# All endpoints: (module, method, path, body)
endpoints = [
    ("health", "GET", "/api/health", None),
    ("health-db", "GET", "/api/health/db", None),
    ("root", "GET", "/", None),
    ("auth", "GET", "/api/auth/me", None),
    ("auth", "GET", "/api/auth/roles", None),
    ("auth", "POST", "/api/auth/logout", {}),
    ("auth", "PUT", "/api/auth/me", {"real_name": "Test Updated"}),
    ("auth", "PATCH", "/api/auth/me/roles", {"role_ids": [1]}),
    ("auth", "PUT", "/api/auth/me/password", {"old_password": "Test@123456", "new_password": "Test@123456"}),
    ("auth", "POST", "/api/auth/register", {"username": "test2", "password": "Test@123", "confirm_password": "Test@123", "real_name": "Test2"}),
    ("users", "GET", "/api/users", None),
    ("users", "PUT", "/api/users/6/status", {"status": "active"}),
    ("users", "PUT", "/api/users/6/roles", {"role_ids": [1]}),
    ("users", "GET", "/api/roles", None),
    ("users", "GET", "/api/permissions", None),
    ("projects", "GET", "/api/projects", None),
    ("projects", "POST", "/api/projects", {"project_name": "Test Project", "description": "Test"}),
    ("projects", "GET", "/api/projects/1", None),
    ("projects", "PUT", "/api/projects/1", {"project_name": "Updated Project"}),
    ("projects", "POST", "/api/projects/1/archive", {}),
    ("projects", "GET", "/api/projects/1/members", None),
    ("projects", "POST", "/api/projects/1/members", {"user_id": 6, "project_role": "member"}),
    ("projects", "PUT", "/api/projects/1/members/1", {"project_role": "leader"}),
    ("projects", "DELETE", "/api/projects/1/members/1", None),
    ("projects", "DELETE", "/api/projects/1", None),
    ("tasks", "GET", "/api/projects/1/tasks", None),
    ("tasks", "POST", "/api/projects/1/tasks", {"task_type_id": 1, "title": "Test Task", "description": "Test"}),
    ("tasks", "GET", "/api/tasks/1", None),
    ("tasks", "PUT", "/api/tasks/1", {"title": "Updated Task"}),
    ("tasks", "GET", "/api/tasks/1/branches", None),
    ("tasks", "POST", "/api/tasks/1/branches", {"branch_name": "test-branch"}),
    ("tasks", "GET", "/api/tasks/1/outputs", None),
    ("tasks", "GET", "/api/outputs/1", None),
    ("tasks", "GET", "/api/outputs/1/timeline", None),
    ("tasks", "POST", "/api/tasks/1/outputs/manual", {"output_title": "Manual", "content": "Test content"}),
    ("tasks", "PUT", "/api/outputs/1", {"content": "Updated content"}),
    ("tasks", "POST", "/api/outputs/1/save-as", {"new_title": "Copy"}),
    ("tasks", "POST", "/api/outputs/1/save-as-new-version", {"content": "New version"}),
    ("tasks", "GET", "/api/outputs/1/comments", None),
    ("tasks", "POST", "/api/outputs/1/comments", {"comment_text": "Nice", "comment_type": "comment"}),
    ("tasks", "PUT", "/api/comments/1/status", {"status": "resolved"}),
    ("tasks", "GET", "/api/outputs/compare?output_id1=1&output_id2=2", None),
    ("tasks", "DELETE", "/api/tasks/1", None),
    ("prompts", "GET", "/api/task-types", None),
    ("prompts", "GET", "/api/prompt-templates", None),
    ("prompts", "POST", "/api/prompt-templates", {"template_name": "Test Template", "task_type_id": 1}),
    ("prompts", "GET", "/api/prompt-templates/1", None),
    ("prompts", "PUT", "/api/prompt-templates/1", {"template_name": "Updated"}),
    ("prompts", "GET", "/api/prompt-templates/1/versions", None),
    ("prompts", "POST", "/api/prompt-templates/1/versions", {"prompt_content": "Test prompt", "change_note": "Initial"}),
    ("prompts", "POST", "/api/prompt-templates/1/versions/1/activate", {}),
    ("prompts", "DELETE", "/api/prompt-templates/1", None),
    ("models", "GET", "/api/model-providers", None),
    ("models", "POST", "/api/model-providers", {"provider_name": "Test", "provider_code": "test_p"}),
    ("models", "GET", "/api/ai-models", None),
    ("models", "POST", "/api/ai-models", {"provider_id": 1, "model_name": "test-m", "display_name": "Test Model"}),
    ("models", "GET", "/api/api-configs", None),
    ("models", "POST", "/api/api-configs", {"provider_id": 1, "config_name": "Test Config", "api_key": "sk-test"}),
    ("invocations", "GET", "/api/invocations", None),
    ("invocations", "GET", "/api/invocations/1", None),
    ("invocations", "POST", "/api/tasks/1/generate", {"model_id": 1, "prompt_version_id": 1}),
    ("reviews", "POST", "/api/outputs/1/submit-review", {}),
    ("reviews", "GET", "/api/reviews/pending", None),
    ("reviews", "GET", "/api/reviews/1", None),
    ("reviews", "POST", "/api/reviews/1/complete", {"review_status": "approved", "review_comment": "OK"}),
    ("reviews", "GET", "/api/issue-tags", None),
    ("artifacts", "POST", "/api/outputs/1/adopt", {"artifact_title": "Adopted", "artifact_type": "doc"}),
    ("artifacts", "GET", "/api/projects/1/artifacts", None),
    ("artifacts", "GET", "/api/artifacts/1", None),
    ("artifacts", "POST", "/api/tasks/1/branches/merge", {"source_output_id": 1, "target_output_id": 2, "merge_strategy": "adopt_source"}),
    ("statistics", "GET", "/api/statistics/overview", None),
    ("statistics", "GET", "/api/statistics/projects", None),
    ("statistics", "GET", "/api/statistics/model-calls", None),
    ("statistics", "GET", "/api/statistics/costs", None),
    ("statistics", "GET", "/api/statistics/reviews", None),
    ("statistics", "GET", "/api/statistics/member-contributions", None),
    ("statistics", "GET", "/api/statistics/recent-activities", None),
    ("statistics", "GET", "/api/statistics/learning-overview", None),
    ("statistics", "GET", "/api/statistics/mastery-distribution", None),
    ("statistics", "GET", "/api/statistics/weak-knowledge-points", None),
    ("statistics", "GET", "/api/statistics/resource-type-distribution", None),
    ("statistics", "GET", "/api/statistics/invocation-trend", None),
    ("statistics", "GET", "/api/statistics/review-rate-by-course", None),
    ("statistics", "GET", "/api/statistics/cost-distribution", None),
    ("logs", "GET", "/api/logs/operation", None),
    ("logs", "GET", "/api/logs/login", None),
    ("profiles", "GET", "/api/profiles/", None),
    ("profiles", "GET", "/api/profiles/1", None),
    ("profiles", "PUT", "/api/profiles/1", {"dominant_style": "visual", "learning_goal": "Test"}),
    ("profiles", "POST", "/api/profiles/1/mastery", {"knowledge_point_id": 1, "mastery_level": 0.8}),
    ("agents", "GET", "/api/agents/list", None),
    ("agents", "GET", "/api/agents/workflow/test-run-1", None),
    ("agents", "POST", "/api/agents/generate", {"student_id": 3, "course_id": 1, "knowledge_point_ids": [1], "resource_type": "lecture", "difficulty": "intermediate"}),
    ("agents", "POST", "/api/agents/save-resource", {"student_id": 3, "course_id": 1, "resource_type": "lecture", "title": "Test Resource", "content": "Test content"}),
    ("learning", "GET", "/api/learning/courses", None),
    ("learning", "GET", "/api/learning/courses/1", None),
    ("learning", "PUT", "/api/learning/courses/1", {"course_name": "Updated Course"}),
    ("learning", "GET", "/api/learning/tasks", None),
    ("learning", "GET", "/api/learning/tasks/1", None),
    ("learning", "GET", "/api/learning/courses/1/learning-path", None),
    ("feedbacks", "GET", "/api/learning/feedbacks", None),
    ("feedbacks", "POST", "/api/learning/feedbacks", {"course_id": 1, "feedback_type": "suggestion", "content": "Great"}),
    ("resources", "GET", "/api/learning/resources", None),
    ("resources", "GET", "/api/learning/resources/1", None),
    ("storage", "GET", "/api/storage/1", None),
]

results = defaultdict(list)

for module, method, path, body in endpoints:
    try:
        if method == "GET":
            resp = requests.get(f"{BASE}{path}", headers=headers, timeout=15)
        elif method == "POST":
            resp = requests.post(f"{BASE}{path}", json=body, headers=headers, timeout=15)
        elif method == "PUT":
            resp = requests.put(f"{BASE}{path}", json=body, headers=headers, timeout=15)
        elif method == "PATCH":
            resp = requests.patch(f"{BASE}{path}", json=body, headers=headers, timeout=15)
        elif method == "DELETE":
            resp = requests.delete(f"{BASE}{path}", headers=headers, timeout=15)

        code = resp.status_code
        try:
            body_data = resp.json()
            msg = body_data.get("message", "")[:80]
        except Exception:
            msg = resp.text[:80]

        status = "OK" if code < 400 else f"FAIL({code})"
        results[module].append((method, path, code, msg, status))
        print(f"[{module:15s}] {method:6s} {path:50s} -> {code} {msg[:60]}")

    except Exception as e:
        results[module].append((method, path, 0, str(e)[:60], "ERROR"))
        print(f"[{module:15s}] {method:6s} {path:50s} -> ERROR: {str(e)[:60]}")

print()
print("=" * 85)
print("API ENDPOINT TEST SUMMARY")
print("=" * 85)

total_ok = 0
total_fail = 0
total_err = 0

for module in sorted(results.keys()):
    tests = results[module]
    ok = sum(1 for t in tests if t[4] == "OK")
    fail = sum(1 for t in tests if t[4].startswith("FAIL"))
    err = sum(1 for t in tests if t[4] == "ERROR")
    total_ok += ok
    total_fail += fail
    total_err += err

    if fail == 0 and err == 0:
        symbol = "  OK  "
    elif err > 0:
        symbol = " ERROR"
    else:
        symbol = " PARTIAL"

    print(f"  {symbol}  {module:15s}: {ok:2d} OK, {fail:2d} FAIL, {err:2d} ERROR  (of {len(tests)})")

total = total_ok + total_fail + total_err
print(f"\n  TOTAL: {total_ok} OK, {total_fail} FAIL, {total_err} ERROR  (of {total})")
print()

# Show only failing endpoints
print("FAILING/ERROR ENDPOINTS:")
print("-" * 85)
for module in sorted(results.keys()):
    for method, path, code, msg, status in results[module]:
        if status != "OK":
            print(f"  [{module}] {method} {path} -> {code} {msg[:70]}")
