from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.domain.schemas.logs import LogsResponse, LogsQuery, AuditLogEntry
from app.domain.services.log_service import LogService

router = APIRouter()

# Instancia singleton del servicio de logs
log_service = LogService()


@router.get("/logs", response_model=LogsResponse)
def get_audit_logs(
    actor: Optional[str] = Query(None, description="Filtrar por actor"),
    action: Optional[str] = Query(None, description="Filtrar por acción (create, update, delete, start, stop, restart)"),
    provider: Optional[str] = Query(None, description="Filtrar por proveedor (aws, azure, gcp, onpremise, oracle)"),
    success: Optional[bool] = Query(None, description="Filtrar por éxito/fallo"),
    vm_id: Optional[str] = Query(None, description="Filtrar por ID de VM"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=200, description="Tamaño de página (máx 200)")
):
 
    try:
        query = LogsQuery(
            actor=actor,
            action=action,
            provider=provider,
            success=success,
            vm_id=vm_id,
            page=page,
            page_size=page_size
        )
        
        logs, total = log_service.get_logs(query)
        
        return LogsResponse(
            logs=logs,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading logs")


@router.get("/logs/recent")
def get_recent_logs(limit: int = Query(100, ge=1, le=500)):
    """
    Obtiene los logs más recientes (para dashboard).
    """
    try:
        logs = log_service.get_recent_logs(limit)
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading recent logs")


@router.get("/logs/stats")
def get_log_statistics():
    """
    Obtiene estadísticas de los logs de auditoría.
    """
    try:
        stats = log_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error calculating log statistics")


@router.get("/logs/actions")
def get_available_actions():
    """
    Obtiene la lista de acciones disponibles para filtrar.
    """
    return {
        "actions": ["create", "update", "delete", "start", "stop", "restart"],
        "providers": ["aws", "azure", "gcp", "onpremise", "oracle"]
    }