import unittest

from fastapi import FastAPI
from pydantic import ValidationError

from app.routers.knowledge import (
    KpLinkVerifyRequest,
    ResourceEvidenceVerifyRequest,
    router,
)


class KnowledgeApiContractTests(unittest.TestCase):
    def test_kp_link_verify_accepts_object_body(self):
        payload = KpLinkVerifyRequest.model_validate({"status": "confirmed"})
        self.assertEqual(payload.status, "confirmed")

    def test_resource_verify_accepts_object_body(self):
        payload = ResourceEvidenceVerifyRequest.model_validate({"status": "verified"})
        self.assertEqual(payload.status, "verified")

    def test_verify_models_reject_unknown_status(self):
        with self.assertRaises(ValidationError):
            KpLinkVerifyRequest.model_validate({"status": "approved"})
        with self.assertRaises(ValidationError):
            ResourceEvidenceVerifyRequest.model_validate({"status": "confirmed"})

    def test_search_query_length_is_bounded(self):
        app = FastAPI()
        app.include_router(router)
        parameters = app.openapi()["paths"]["/knowledge/search"]["get"]["parameters"]
        query_schema = next(
            parameter["schema"]
            for parameter in parameters
            if parameter["name"] == "query"
        )

        self.assertEqual(query_schema["minLength"], 1)
        self.assertEqual(query_schema["maxLength"], 2000)


if __name__ == "__main__":
    unittest.main()
