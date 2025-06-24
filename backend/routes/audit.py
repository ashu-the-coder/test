from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from services.audit import AuditService
from models.audit import AuditLog
from middleware.rbac import verify_user_role, security
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()
audit_service = AuditService()

@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLog])
@verify_user_role(["admin", "inventory_manager", "supply_chain_head"])
async def get_entity_audit_logs(
    entity_type: str,
    entity_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get audit logs for a specific entity
    """
    return audit_service.get_entity_audit_trail(entity_type, entity_id)

@router.get("/search", response_model=List[AuditLog])
@verify_user_role(["admin"])
async def search_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    changed_by: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Search audit logs with various filters
    This endpoint is admin-only
    """
    return audit_service.get_audit_trail(
        entity_type=entity_type,
        entity_id=entity_id,
        changed_by=changed_by,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        skip=skip
    )
