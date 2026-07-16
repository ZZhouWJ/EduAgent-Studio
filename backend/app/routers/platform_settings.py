"""平台配置 API。"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.services.platform_settings_service import PlatformSettingsService
from app.utils.dependencies import require_role
from app.utils.response import success_response

router = APIRouter(prefix="/platform-settings", tags=["平台配置"])


class UpdateGovernanceSettingsRequest(BaseModel):
    fact_consistency_threshold: int = Field(..., ge=0, le=100)
    citation_coverage_threshold: int = Field(..., ge=0, le=100)
    hourly_call_limit: int = Field(..., ge=1, le=10000)
    sensitive_content_enabled: bool


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/governance")
async def get_governance_settings(
    user: dict = Depends(require_role("admin")),
) -> dict:
    return success_response(data=PlatformSettingsService().get_governance())


@router.put("/governance")
async def update_governance_settings(
    body: UpdateGovernanceSettingsRequest,
    request: Request,
    user: dict = Depends(require_role("admin")),
) -> dict:
    result = PlatformSettingsService().update_governance(
        user=user,
        fact_consistency_threshold=body.fact_consistency_threshold,
        citation_coverage_threshold=body.citation_coverage_threshold,
        hourly_call_limit=body.hourly_call_limit,
        sensitive_content_enabled=body.sensitive_content_enabled,
        ip_address=_get_client_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
    )
    return success_response(data=result, message="治理规则已更新")
