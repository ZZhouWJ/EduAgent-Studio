import unittest

from pydantic import ValidationError

from app.routers.knowledge import KpLinkVerifyRequest, ResourceEvidenceVerifyRequest


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


if __name__ == "__main__":
    unittest.main()
