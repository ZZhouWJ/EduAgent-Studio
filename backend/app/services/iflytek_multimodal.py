"""
讯飞多模态 API 封装（P1/P2）

包含：图片理解 / 图片生成 / 文本改写 / OCR / TTS
认证与大模型共用 HMAC-SHA256 签名。

各 API 文档：https://www.xfyun.cn/doc/
"""

import base64
import hashlib
import hmac
import json
import logging
import threading
import time
from typing import Optional
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import httpx
import websocket

logger = logging.getLogger(__name__)

# 各 API 地址（讯飞控制台查看具体地址）
IMAGE_UNDERSTAND_URL = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"
IMAGE_GENERATE_URL = "https://oa.aiadv.xf-yun.com/v1/generate"
TEXT_REWRITE_URL = "https://oa.aiadv.xf-yun.com/v1/analysis"
OCR_URL = "https://oa.aiadv.xf-yun.com/v1/ocr"
TTS_URL = "wss://tts-api.xfyun.cn/v2/tts"


def _build_ws_url(ws_url: str, api_key: str, api_secret: str) -> str:
    """构建讯飞 WebSocket 鉴权 URL（HMAC-SHA256）。"""
    host = urlparse(ws_url).netloc
    path = urlparse(ws_url).path
    date = format_date_time(time.time())

    sign_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    sig_sha = hmac.new(
        api_secret.encode("utf-8"),
        sign_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    sig_b64 = base64.b64encode(sig_sha).decode("utf-8")

    auth_origin = (
        f'api_key="{api_key}", '
        f'algorithm="hmac-sha256", '
        f'headers="host date request-line", '
        f'signature="{sig_b64}"'
    )
    auth = base64.b64encode(auth_origin.encode("utf-8")).decode("utf-8")

    return f"{ws_url}?{urlencode({'authorization': auth, 'date': date, 'host': host})}"


def _auth(app_id: str, api_secret: str) -> dict:
    """生成讯飞 HMAC-SHA1 认证头（旧接口使用）。"""
    ts = str(int(time.time()))
    sign_str = f"{app_id}{ts}"
    sign = base64.b64encode(
        hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha1).digest()
    ).decode()
    return {"app_id": app_id, "timestamp": ts, "sign": sign}


def _post(url: str, app_id: str, api_key: str, api_secret: str,
          payload: dict, timeout: float = 30.0) -> dict:
    """通用 POST 请求（含讯飞认证）。"""
    auth = _auth(app_id, api_secret)
    headers = {"Content-Type": "application/json"}
    body = {"header": auth, "payload": payload}
    resp = httpx.post(url, headers=headers, json=body, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# 图片理解
# ---------------------------------------------------------------------------

def image_understand(
    image_base64: str,
    question: str = "详细描述这张图片的内容",
    app_id: str = "",
    api_key: str = "",
    api_secret: str = "",
) -> str:
    """
    讯飞图片理解：上传图片 + 问题，通过 WebSocket 获取 AI 分析结果。

    Args:
        image_base64: 图片 base64 编码（不含 data:image 前缀）
        question: 对图片的提问
        app_id/api_key/api_secret: 讯飞凭证

    Returns:
        AI 分析文本，失败返回空字符串
    """
    if not app_id or not api_key or not api_secret:
        logger.warning("[IFlyTek ImageUnderstand] 凭证未配置")
        return ""

    ws_url = _build_ws_url(IMAGE_UNDERSTAND_URL, api_key, api_secret)
    result: list[str] = []
    error_msg: list[str] = []

    def on_open(ws):
        data = json.dumps({
            "header": {"app_id": app_id},
            "parameter": {
                "chat": {
                    "domain": "imagev3",
                    "temperature": 0.5,
                    "top_k": 4,
                    "max_tokens": 2048,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": image_base64, "content_type": "image"},
                        {"role": "user", "content": question, "content_type": "text"},
                    ]
                }
            },
        })
        ws.send(data)

    def on_message(ws, message):
        data = json.loads(message)
        code = data.get("header", {}).get("code", 0)
        if code != 0:
            error_msg.append(data.get("header", {}).get("message", f"code={code}"))
            ws.close()
            return
        choices = data.get("payload", {}).get("choices", {})
        status = choices.get("status", 0)
        content = choices.get("text", [{}])[0].get("content", "")
        result.append(content)
        if status == 2:  # 最后一个结果
            ws.close()

    def on_error(ws, error):
        error_msg.append(str(error))

    try:
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
        )
        timeout_guard = threading.Timer(60, ws.close)
        timeout_guard.start()
        try:
            ws.run_forever(ping_interval=20, ping_timeout=10)
        finally:
            timeout_guard.cancel()

        if error_msg:
            logger.error(f"[IFlyTek ImageUnderstand] error: {error_msg[0]}")
            return ""

        answer = "".join(result)
        logger.info(f"[IFlyTek ImageUnderstand] result={answer[:80]}")
        return answer

    except Exception as e:
        logger.error(f"[IFlyTek ImageUnderstand] failed: {e}")
        return ""


# ---------------------------------------------------------------------------
# 图片生成
# ---------------------------------------------------------------------------

def generate_image(
    prompt: str,
    style: str = "动漫风格",
    resolution: str = "1024*1024",
    app_id: str = "",
    api_key: str = "",
    api_secret: str = "",
) -> str:
    """
    讯飞图片生成：返回生成的图片 Base64。
    """
    if not app_id or not api_key or not api_secret:
        logger.warning("[IFlyTek ImageGenerate] 凭证未配置")
        return ""

    try:
        payload = {
            "prompt": prompt,
            "style": style,
            "resolution": resolution,
        }
        data = _post(IMAGE_GENERATE_URL, app_id, api_key, api_secret, payload)
        img = data.get("payload", {}).get("image", "")
        logger.info(f"[IFlyTek ImageGenerate] OK, length={len(img)}")
        return img
    except Exception as e:
        logger.error(f"[IFlyTek ImageGenerate failed: {e}")
        return ""


# ---------------------------------------------------------------------------
# 文本改写
# ---------------------------------------------------------------------------

def rewrite_text(
    text: str,
    style: str = "正式",
    app_id: str = "",
    api_key: str = "",
    api_secret: str = "",
) -> str:
    """
    讯飞文本改写/润色。
    """
    if not app_id or not api_key or not api_secret:
        logger.warning("[IFlyTek TextRewrite] 凭证未配置")
        return ""

    try:
        payload = {
            "text": text,
            "style": style,
        }
        data = _post(TEXT_REWRITE_URL, app_id, api_key, api_secret, payload)
        return data.get("payload", {}).get("result", text)
    except Exception as e:
        logger.error(f"[IFlyTek TextRewrite failed: {e}")
        return text  # 失败时原样返回


# ---------------------------------------------------------------------------
# OCR 文字识别
# ---------------------------------------------------------------------------

def recognize_text(
    image_base64: str,
    app_id: str = "",
    api_key: str = "",
    api_secret: str = "",
) -> str:
    """
    讯飞通用文字识别 OCR：图片 Base64 → 图片中的文字。
    """
    if not app_id or not api_key or not api_secret:
        logger.warning("[IFlyTek OCR] 凭证未配置")
        return ""

    try:
        payload = {
            "image": image_base64,
        }
        data = _post(OCR_URL, app_id, api_key, api_secret, payload)
        texts = data.get("payload", {}).get("text", [])
        return "\n".join(texts) if isinstance(texts, list) else str(texts)
    except Exception as e:
        logger.error(f"[IFlyTek OCR failed: {e}")
        return ""


# ---------------------------------------------------------------------------
# TTS 语音合成
# ---------------------------------------------------------------------------

def text_to_speech(
    text: str,
    voice: str = "xiaoyan",
    speed: int = 50,
    volume: int = 50,
    pitch: int = 50,
    app_id: str = "",
    api_key: str = "",
    api_secret: str = "",
) -> bytes:
    """
    讯飞语音合成：文本 → 音频 bytes（MP3/WAV）。

    Returns:
        音频二进制数据，失败返回空 bytes
    """
    if not app_id or not api_key or not api_secret:
        logger.warning("[IFlyTek TTS] 凭证未配置")
        return b""

    try:
        if not text.strip() or len(text.encode("utf-8")) >= 8000:
            logger.warning("[IFlyTek TTS] 文本为空或超过 8000 字节")
            return b""

        ws_url = _build_ws_url(TTS_URL, api_key, api_secret)
        chunks: list[bytes] = []
        errors: list[str] = []
        body = {
            "common": {"app_id": app_id},
            "business": {
                "aue": "lame",
                "auf": "audio/L16;rate=16000",
                "vcn": voice,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "tte": "UTF8",
            },
            "data": {
                "status": 2,
                "text": base64.b64encode(text.encode()).decode(),
            },
        }
        def on_open(ws):
            ws.send(json.dumps(body))

        def on_message(ws, message):
            result = json.loads(message)
            code = result.get("code", 0)
            if code != 0:
                errors.append(result.get("message", f"code={code}"))
                ws.close()
                return
            data = result.get("data", {})
            audio_b64 = data.get("audio", "")
            if audio_b64:
                chunks.append(base64.b64decode(audio_b64))
            if data.get("status") == 2:
                ws.close()

        def on_error(ws, error):
            errors.append(str(error))

        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
        )
        timeout_guard = threading.Timer(60, ws.close)
        timeout_guard.start()
        try:
            ws.run_forever(ping_interval=20, ping_timeout=10)
        finally:
            timeout_guard.cancel()

        if errors:
            logger.error(f"[IFlyTek TTS] error: {errors[0]}")
            return b""
        return b"".join(chunks)

    except Exception as e:
        logger.error(f"[IFlyTek TTS failed: {e}")
        return b""
