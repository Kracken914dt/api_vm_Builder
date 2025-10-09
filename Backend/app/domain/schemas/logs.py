from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AuditLogEntry(BaseModel):
    timestamp: str
    actor: str
    action: str
    vm_id: str
    provider: str
    success: bool
    details: Optional[dict] = None


class LogsResponse(BaseModel):
    logs: List[AuditLogEntry]
    total: int
    page: int
    page_size: int


class LogsQuery(BaseModel):
    actor: Optional[str] = None
    action: Optional[str] = None
    provider: Optional[str] = None
    success: Optional[bool] = None
    vm_id: Optional[str] = None
    page: int = 1
    page_size: int = 50