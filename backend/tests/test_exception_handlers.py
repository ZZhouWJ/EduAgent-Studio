import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.utils.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    register_exception_handlers,
)


class ExceptionHandlerTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/error/{kind}")
        async def raise_error(kind: str):
            errors = {
                "validation": ValidationException("invalid"),
                "forbidden": ForbiddenException("forbidden"),
                "unauthorized": UnauthorizedException("unauthorized"),
                "missing": NotFoundException("missing"),
                "conflict": ConflictException("conflict"),
            }
            raise errors[kind]

        self.client = TestClient(app, raise_server_exceptions=False)

    def test_business_exceptions_use_semantic_http_statuses(self):
        expected = {
            "validation": (400, 4000),
            "forbidden": (403, 4001),
            "unauthorized": (401, 4002),
            "missing": (404, 4003),
            "conflict": (409, 4004),
        }

        for kind, (status, code) in expected.items():
            with self.subTest(kind=kind):
                response = self.client.get(f"/error/{kind}")
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()["code"], code)


if __name__ == "__main__":
    unittest.main()
