from typing import List
from app.domain.schemas import (
    VMCreateRequest,
    VMDTO,
    VMUpdateRequest,
    VMActionRequest,
)
from app.domain.factories import get_factory
from app.domain.ports import VMRepositoryPort
from app.infrastructure.logger import audit_log


class VMService:
    def __init__(self, repo: VMRepositoryPort):
        self.repo = repo

    def create_vm(self, data: VMCreateRequest) -> VMDTO:
        factory = get_factory(data.provider)
        # data.params ahora es un modelo Pydantic específico; pasamos dict limpio
        vm = factory.provision(data.name, data.params.model_dump())
        self.repo.save(vm)
        audit_log(
            actor=data.requested_by or "system",
            action="create",
            vm_id=vm.id,
            provider=vm.provider.value,
            success=True,
            details={"name": vm.name},
        )
        return vm

    def update_vm(self, vm_id: str, changes: VMUpdateRequest) -> VMDTO:
        vm = self.repo.get(vm_id)
        factory = get_factory(vm.provider)
        vm = factory.update(vm, changes)
        self.repo.save(vm)
        audit_log(
            actor="system",
            action="update",
            vm_id=vm.id,
            provider=vm.provider.value,
            success=True,
            details=changes.dict(exclude_none=True),
        )
        return vm

    def delete_vm(self, vm_id: str) -> None:
        vm = self.repo.get(vm_id)
        self.repo.delete(vm_id)
        audit_log(
            actor="system",
            action="delete",
            vm_id=vm.id,
            provider=vm.provider.value,
            success=True,
            details=None,
        )

    def apply_action(self, vm_id: str, action_req: VMActionRequest) -> VMDTO:
        vm = self.repo.get(vm_id)
        factory = get_factory(vm.provider)
        vm = factory.apply_action(vm, action_req.action)
        self.repo.save(vm)
        audit_log(
            actor=action_req.requested_by or "system",
            action=action_req.action,
            vm_id=vm.id,
            provider=vm.provider.value,
            success=True,
            details=None,
        )
        return vm

    def get_vm(self, vm_id: str) -> VMDTO:
        return self.repo.get(vm_id)

    def list_vms(self) -> List[VMDTO]:
        return self.repo.list()
