from app.domain.services import VMService
from app.infrastructure.repository import VMRepository

# Contenedor simple para inyección de dependencias (DIP)
_repo = VMRepository()
_service = VMService(repo=_repo)


def get_vm_service() -> VMService:
    return _service
