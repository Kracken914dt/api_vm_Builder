from fastapi import APIRouter, Depends, HTTPException
from app.domain.schemas import (
    VMCreateRequest,
    VMResponse,
    VMUpdateRequest,
    VMActionRequest,
    VMListResponse,
    VMBuildRequest,
)
from app.core.container import get_vm_service
from app.domain.services import VMService
from app.infrastructure.logger import audit_log

router = APIRouter()


@router.post("/create", response_model=VMResponse)
def create_vm(
    payload: VMCreateRequest,
    service: VMService = Depends(get_vm_service),
):
    try:
        vm = service.create_vm(payload)
        return VMResponse(success=True, vm=vm)
    except ValueError as e:
        # Log de error de validación sin datos sensibles
        audit_log(
            actor=payload.requested_by or "system",
            action="create",
            vm_id="n/a",
            provider=payload.provider.value,
            success=False,
            details={"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        audit_log(
            actor=payload.requested_by or "system",
            action="create",
            vm_id="n/a",
            provider=payload.provider.value,
            success=False,
            details={"error": "internal_error"},
        )
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/build", response_model=VMResponse)
def build_vm(
    payload: VMBuildRequest,
    service: VMService = Depends(get_vm_service),
):
    try:
        vm = service.build_vm(payload)
        return VMResponse(success=True, vm=vm)
    except ValueError as e:
        audit_log(
            actor="system",
            action="create(builder)",
            vm_id="n/a",
            provider=payload.provider.value,
            success=False,
            details={"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.put("/{vm_id}", response_model=VMResponse)
def update_vm(
    vm_id: str,
    payload: VMUpdateRequest,
    service: VMService = Depends(get_vm_service),
):
    try:
        vm = service.update_vm(vm_id, payload)
        return VMResponse(success=True, vm=vm)
    except KeyError:
        audit_log(
            actor="system",
            action="update",
            vm_id=vm_id,
            provider="unknown",
            success=False,
            details={"error": "not_found"},
        )
        raise HTTPException(status_code=404, detail="VM not found")
    except ValueError as e:
        audit_log(
            actor="system",
            action="update",
            vm_id=vm_id,
            provider="unknown",
            success=False,
            details={"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{vm_id}", response_model=VMResponse)
def delete_vm(
    vm_id: str,
    service: VMService = Depends(get_vm_service),
):
    try:
        service.delete_vm(vm_id)
        return VMResponse(success=True, vm=None)
    except KeyError:
        audit_log(
            actor="system",
            action="delete",
            vm_id=vm_id,
            provider="unknown",
            success=False,
            details={"error": "not_found"},
        )
        raise HTTPException(status_code=404, detail="VM not found")


@router.post("/{vm_id}/action", response_model=VMResponse)
def action_vm(
    vm_id: str,
    payload: VMActionRequest,
    service: VMService = Depends(get_vm_service),
):
    try:
        vm = service.apply_action(vm_id, payload)
        return VMResponse(success=True, vm=vm)
    except KeyError:
        audit_log(
            actor=payload.requested_by or "system",
            action=payload.action,
            vm_id=vm_id,
            provider="unknown",
            success=False,
            details={"error": "not_found"},
        )
        raise HTTPException(status_code=404, detail="VM not found")
    except ValueError as e:
        audit_log(
            actor=payload.requested_by or "system",
            action=payload.action,
            vm_id=vm_id,
            provider="unknown",
            success=False,
            details={"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{vm_id}", response_model=VMResponse)
def get_vm(
    vm_id: str,
    service: VMService = Depends(get_vm_service),
):
    try:
        vm = service.get_vm(vm_id)
        return VMResponse(success=True, vm=vm)
    except KeyError:
        raise HTTPException(status_code=404, detail="VM not found")


@router.get("/", response_model=VMListResponse)
def list_vms(service: VMService = Depends(get_vm_service)):
    vms = service.list_vms()
    return VMListResponse(items=vms)
