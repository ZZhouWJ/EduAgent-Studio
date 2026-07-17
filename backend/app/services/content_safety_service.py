"""Deterministic safety checks applied before and after model calls."""

import json
import re
from dataclasses import dataclass
from threading import RLock
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class SafetyFinding:
    category: str


_BLOCK_PATTERNS = (
    (
        "dangerous_instructions",
        re.compile(
            r"(?:如何|怎么|教程|步骤|方法).{0,20}"
            r"(?:制造|制作|自制).{0,8}(?:炸弹|爆炸物|毒品)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "cyber_abuse",
        re.compile(
            r"(?:如何|怎么|教程|步骤).{0,20}"
            r"(?:窃取|盗取).{0,8}(?:密码|令牌|账号)|"
            r"(?:绕过|破解).{0,8}(?:身份认证|登录|访问控制)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "self_harm_instructions",
        re.compile(
            r"(?:如何|怎么|步骤|方法).{0,12}(?:自杀|自残)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "sexual_content_involving_minors",
        re.compile(
            r"(?:未成年|儿童).{0,12}(?:色情|性行为)|"
            r"(?:色情|性行为).{0,12}(?:未成年|儿童)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "prompt_injection",
        re.compile(
            r"(?:忽略|无视).{0,12}(?:系统|之前|以上).{0,12}(?:指令|提示词)|"
            r"(?:输出|泄露|显示).{0,12}(?:系统提示词|开发者消息)",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "credential_exposure",
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
            r"\bsk-[A-Za-z0-9_-]{20,}\b|\bAKIA[0-9A-Z]{16}\b",
        ),
    ),
)


class ContentSafetyPolicy:
    def __init__(self) -> None:
        self._enabled = True
        self._lock = RLock()

    @property
    def enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._enabled = bool(enabled)

    def scan_text(self, text: str) -> Optional[SafetyFinding]:
        if not self.enabled or not text:
            return None
        for category, pattern in _BLOCK_PATTERNS:
            if pattern.search(text):
                return SafetyFinding(category=category)
        return None

    def scan_messages(self, messages: Iterable[dict[str, Any]]) -> Optional[SafetyFinding]:
        user_content = "\n".join(
            str(message.get("content") or "")
            for message in messages
            if message.get("role") == "user"
        )
        return self.scan_text(user_content)

    def scan_output(
        self,
        content: str,
        tool_calls: Optional[list[dict[str, Any]]],
    ) -> Optional[SafetyFinding]:
        finding = self.scan_text(content)
        if finding or not tool_calls:
            return finding
        return self.scan_text(json.dumps(tool_calls, ensure_ascii=False, default=str))


content_safety_policy = ContentSafetyPolicy()
