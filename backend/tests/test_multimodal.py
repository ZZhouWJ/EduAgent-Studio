import unittest
from io import BytesIO
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.routers.multimodal import understand_image
from app.services.iflytek_multimodal import TTS_URL, _build_ws_url, text_to_speech


class MultimodalTests(unittest.IsolatedAsyncioTestCase):
    def test_builds_signed_official_tts_websocket_url(self):
        signed = _build_ws_url(TTS_URL, "api-key", "api-secret")
        parsed = urlparse(signed)
        query = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, "wss")
        self.assertEqual(parsed.netloc, "tts-api.xfyun.cn")
        self.assertEqual(parsed.path, "/v2/tts")
        self.assertEqual(query["host"], ["tts-api.xfyun.cn"])
        self.assertIn("authorization", query)

    def test_tts_without_credentials_never_calls_the_network(self):
        self.assertEqual(text_to_speech("测试"), b"")

    async def test_image_endpoint_rejects_non_image_uploads(self):
        upload = UploadFile(
            filename="notes.txt",
            file=BytesIO(b"not an image"),
            headers=Headers({"content-type": "text/plain"}),
        )

        with self.assertRaises(HTTPException) as caught:
            await understand_image(upload, "分析内容", {"user_id": 1})

        self.assertEqual(caught.exception.status_code, 415)


if __name__ == "__main__":
    unittest.main()
