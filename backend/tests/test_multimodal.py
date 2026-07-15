import unittest
from io import BytesIO
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.routers.multimodal import understand_image
from app.services.iflytek_multimodal import (
    IMAGE_GENERATE_URL,
    TTS_URL,
    _build_ws_url,
    generate_image,
    text_to_speech,
)


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

    @patch("app.services.iflytek_multimodal.httpx.post")
    def test_image_generation_uses_official_signed_endpoint(self, post: Mock):
        response = Mock()
        response.json.return_value = {
            "header": {"code": 0},
            "payload": {
                "choices": {"text": [{"content": "encoded-image"}]}
            },
        }
        post.return_value = response

        result = generate_image(
            prompt="数据库事务流程图",
            style="教学插画",
            resolution="640*480",
            app_id="app-id",
            api_key="api-key",
            api_secret="api-secret",
        )

        self.assertEqual(result, "encoded-image")
        request_url = post.call_args.args[0]
        request_body = post.call_args.kwargs["json"]
        self.assertTrue(request_url.startswith(f"{IMAGE_GENERATE_URL}?"))
        self.assertEqual(request_body["parameter"]["chat"]["width"], 640)
        self.assertEqual(request_body["parameter"]["chat"]["height"], 480)
        self.assertEqual(
            request_body["payload"]["message"]["text"][0]["content"],
            "教学插画：数据库事务流程图",
        )
        response.raise_for_status.assert_called_once()

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
