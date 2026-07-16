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

    def test_nginx_sets_browser_security_boundaries(self):
        nginx = (ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")

        for header in (
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Cross-Origin-Opener-Policy",
            "Permissions-Policy",
            "Content-Security-Policy",
        ):
            self.assertIn(f"add_header {header}", nginx)
        for directive in (
            "default-src 'self'",
            "script-src 'self'",
            "connect-src 'self'",
            "object-src 'none'",
            "frame-ancestors 'self'",
        ):
            self.assertIn(directive, nginx)


if __name__ == "__main__":
    unittest.main()
