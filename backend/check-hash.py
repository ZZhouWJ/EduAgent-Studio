import sys
sys.path.insert(0, r"e:\DatabaseManagementPractice\AI-Collab-Audit-System\backend")

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hash_db = "$2b$12$ShxG2SvnL1QcViFPuMRqHO.T8jCQgOpdWBJdYAwhVn9QgnVRCJB4O"

candidates = [
    "Admin@123456",
    "admin",
    "Admin@123",
    "admin123",
    "Admin123",
    "admin123456",
    "Admin@1234567",
    "admin888",
    "Admin@admin",
    "admin_admin",
    "admin@123456",
]

print("Testing bcrypt hash from database:")
print(f"Hash: {hash_db}")
print()
for pwd in candidates:
    result = pwd_context.verify(pwd, hash_db)
    print(f"  '{pwd}' -> {result}")
    if result:
        print(f"\n=== MATCH FOUND: '{pwd}' ===")
        break
