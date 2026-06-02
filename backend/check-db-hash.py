import sys
sys.path.insert(0, r"e:\DatabaseManagementPractice\AI-Collab-Audit-System\backend")

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Actual hash from DB
hash_db = "$2b$12$dijkEKcv4ec2/WSH3UF7p.opuA43BpEawqnlramT1Dt39VKwDRvR2"

# Common test passwords
candidates = [
    "admin", "123456", "password", "admin123",
    "Admin@123456", "Admin@123", "Admin@1234567",
    "admin888", "Admin@admin", "admin@123456",
    "admin123456", "Admin123", "Admin123456",
    "root", "root123", "Root@123", "rootadmin",
    "ai_collab", "ai-admin", "Ai@123456",
    "mysql", "mysql123",
    "a", "test", "test123", "test@123",
]

print(f"Hash: {hash_db}")
print()
for pwd in candidates:
    try:
        result = pwd_context.verify(pwd, hash_db)
        if result:
            print(f"=== MATCH: '{pwd}' ===")
            sys.exit(0)
    except Exception as e:
        print(f"  '{pwd}' -> error: {e}")

print("No match found in candidates")
