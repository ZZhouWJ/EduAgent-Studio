from pathlib import Path
import re
import unittest

from app.services.knowledge_service import MAX_MATERIAL_SIZE


ROOT = Path(__file__).resolve().parents[2]


class DeploymentContractTests(unittest.TestCase):
    def test_nginx_accepts_the_backend_material_upload_limit(self):
        nginx = (ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")
        match = re.search(r"client_max_body_size\s+(\d+)m;", nginx)

        self.assertIsNotNone(match)
        gateway_limit = int(match.group(1)) * 1024 * 1024
        self.assertGreater(gateway_limit, MAX_MATERIAL_SIZE)
        self.assertLessEqual(gateway_limit, MAX_MATERIAL_SIZE + 2 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
