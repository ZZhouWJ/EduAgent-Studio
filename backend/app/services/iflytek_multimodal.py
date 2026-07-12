"""
讯飞多模态 API 封装（P1/P2）

包含：STT / 图片理解 / 图片生成 / 文本改写 / OCR / TTS
认证与大模型共用 HMAC-SHA1 签名。

各 API 文档：https://www.xfyun.cn/doc/
"""

import base64
import hashlib
import hmac
import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# 各 API 地址（讯飞控制台查看具体地址）
STT_URL = "https://队伍建设-api.xf-yun.com/asr吐出"
IMAGE_UNDERSTAND_URL = "https://oa.aiadv.xf-yun.com/v1/analysis"
IMAGE_GENERATE_URL = "https://oa.aiadv.xf-yun.com/v1/generate"
TEXT_REWRITE_URL = "https://oa.aiadv.xf-yun.com/v1/analysis"
OCR_URL = "https://oa.aiadv.xf-yun.com/v1/ocr"
TTS_URL = "https://队伍建设-api.xf-yun.com/tts_post"


def _auth(app_id: str, api_secret: str) -> dict:
    """生成讯飞 HMAC-SHA1 认证头。"""
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
# STT — 语音听写（Speech-to-Text）
# ---------------------------------------------------------------------------

def speech_to_text(
    audio_data: bytes,
    format: str = "wav",
    app_id: str = "",
    api_key: str = "",
    api_secret: str = "",
) -> str:
    """
    讯飞语音听写：音频 bytes → 中文文本。

    Args:
        audio_data: 音频文件二进制（建议 16kHz 16bit PCM/WAV）
        format: 音频格式，"wav" / "pcm" / "opus" 等
        app_id/api_key/api_secret: 讯飞凭证（同大模型）
    Returns:
        识别出的中文文本，失败返回空字符串
    """
    if not app_id or not api_key or not api_secret:
        logger.warning("[IFlyTek STT] 凭证未配置")
        return ""

    try:
        audio_b64 = base64.b64encode(audio_data).decode()
        payload = {
            "data": {
                "status": 2,
                "format": format,
                "encoding": "raw",
                "sample": 16000,
                "bits": 16,
                "channel": 1,
                "token": api_key,
                "content": audio_b64,
            }
        }
        data = _post(STT_URL, app_id, api_key, api_secret, payload)

        code = data.get("header", {}).get("code", 0)
        if code != 0:
            logger.warning(f"[IFlyTek STT] code={code}: {data.get('header', {}).get('message')}")
            return ""

        texts = data.get("payload", {}).get("result", {}).get("ws", [])
        return "".join(w.get("cw", []).get("w", "") for w in texts if w.get("cw"))

    except Exception as e:
        logger.error(f"[IFlyTek STT] failed: {e}")
        return ""


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
    讯飞图片理解：发送图片 + 问题，返回 AI 分析结果。
    """
    if not app_id or not api_key or not api_secret:
        logger.warning("[IFlyTek ImageUnderstand] 凭证未配置")
        return ""

    try:
        payload = {
            "question": question,
            "image": image_base64,
        }
        data = _post(IMAGE_UNDERSTAND_URL, app_id, api_key, api_secret, payload)
        result = data.get("payload", {}).get("result", "")
        logger.info(f"[IFlyTek ImageUnderstand] result={result[:50]}")
        return result
    except Exception as e:
        logger.error(f"[IFlyTek ImageUnderstand failed: {e}")
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
        auth = _auth(app_id, api_secret)
        body = {
            "common": {"app_id": auth["app_id"]},
            "business": {
                "aue": "lame",
                "auf": "audio/L16;rate=16000",
                "voice_name": voice,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "tts_audio_settings": {"aue": "lame"},
            },
            "data": {
                "status": 2,
                "text": base64.b64encode(text.encode()).decode(),
            },
        }
        headers = {"Content-Type": "application/json"}
        resp = httpx.post(TTS_URL, headers=headers, json=body, timeout=30.0)
        resp.raise_for_status()
        result = resp.json()

        code = result.get("header", {}).get("code", 0)
        if code != 0:
            logger.warning(f"[IFlyTek TTS] code={code}")
            return b""

        audio_b64 = result.get("payload", {}).get("audio", "")
        return base64.b64decode(audio_b64) if audio_b64 else b""

    except Exception as e:
        logger.error(f"[IFlyTek TTS failed: {e}")
        return b""
