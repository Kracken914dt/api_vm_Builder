from __future__ import annotations
from typing import List, Dict
from app.domain.schemas import VMDTO
from app.domain.ports import VMRepositoryPort


class VMRepository(VMRepositoryPort):
    """Repositorio en memoria (dict) para simular persistencia sin BD."""

    def __init__(self):
        self._store: Dict[str, VMDTO] = {}

    def save(self, vm: VMDTO) -> None:
        self._store[vm.id] = vm

    def get(self, vm_id: str) -> VMDTO:
        vm = self._store.get(vm_id)
        if not vm:
            raise KeyError("VM not found")
        return vm

    def delete(self, vm_id: str) -> None:
        if vm_id not in self._store:
            raise KeyError("VM not found")
        del self._store[vm_id]

    def list(self) -> List[VMDTO]:
        return list(self._store.values())
