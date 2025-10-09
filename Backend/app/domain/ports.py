from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from app.domain.schemas import VMDTO


class VMRepositoryPort(ABC):
    @abstractmethod
    def save(self, vm: VMDTO) -> None: ...

    @abstractmethod
    def get(self, vm_id: str) -> VMDTO: ...

    @abstractmethod
    def delete(self, vm_id: str) -> None: ...

    @abstractmethod
    def list(self) -> List[VMDTO]: ...
