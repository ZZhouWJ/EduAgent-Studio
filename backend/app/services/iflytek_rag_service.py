"""
讯飞星火知识库 ChatDoc API（RAG 检索）

讯飞 ChatDoc API 文档：https://www.xfyun.cn/doc/spark/ChatDoc-API.html

认证与大模型相同：HMAC-SHA1 签名。
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

CHATDOC_API_URL = "https://spark-api.xf-yun.com/document/chat"


def _generate_auth(app_id: str, api_secret: str) -> Dict[str, str]:
    """生成讯飞 HMAC-SHA1 认证参数。"""
    timestamp = str(int(time.time()))
    sign_str = f"{app_id}{timestamp}"
    sign = base64.b64encode(
        hmac.new(
            api_secret.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode("utf-8")
    return {"app_id": app_id, "timestamp": timestamp, "sign": sign}


def chatdoc_retrieve(
    query: str,
    doc_id: str,
    app_id: str,
    api_key: str,
    api_secret: str,
    top_k: int = 5,
) -> str:
    """
    调用讯飞 ChatDoc API 对知识库进行问答检索。

    Args:
        query: 用户问题（检索词）
        doc_id: 讯飞控制台创建的知识库 ID
        app_id: 讯飞应用 APPID
        api_key: 讯飞应用 APIKey
        api_secret: 讯飞应用 APISecret
        top_k: 返回的最相关段落数量

    Returns:
        检索到的文本片段（多段用 \\n---\\n 连接），若无结果则返回空字符串
    """
    auth = _generate_auth(app_id, api_secret)

    payload = {
        "header": {
            "app_id": auth["app_id"],
            "timestamp": auth["timestamp"],
            "sign": auth["sign"],
        },
        "payload": {
            "question": {
                "template": "",
                "text": query,
                "top_k": top_k,
            }
        },
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = httpx.post(CHATDOC_API_URL, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        code = data.get("header", {}).get("code", 0)
        if code != 0:
            logger.warning(f"[IFlyTek ChatDoc] API error code={code}: {data.get('header', {}).get('message', '')}")
            return ""

        # 解析检索结果
        texts: List[str] = []
        # 讯飞 ChatDoc 返回格式：{"payload": {"answer": {"text": "相关段落..."}}}
        answer_text = (
            data.get("payload", {})
            .get("answer", {})
            .get("text", "")
        )
        if answer_text:
            texts.append(answer_text)

        # 也可能有多段引用，逐段提取
        chunks = (
            data.get("payload", {})
            .get("context", {})
            .get("paragraphs", [])
        )
        for chunk in chunks[:top_k]:
            content = chunk.get("content", "") or chunk.get("text", "")
            if content and content not in texts:
                texts.append(content)

        result = "\n---\n".join(texts)
        logger.info(f"[IFlyTek ChatDoc] retrieved {len(texts)} fragments for query='{query[:30]}...'")
        return result

    except httpx.HTTPStatusError as e:
        logger.error(f"[IFlyTek ChatDoc] HTTP error: {e.response.status_code} - {e.response.text}")
        return ""
    except Exception as e:
        logger.error(f"[IFlyTek ChatDoc] call failed: {e}")
        return ""
