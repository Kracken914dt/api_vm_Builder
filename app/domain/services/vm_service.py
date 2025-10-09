from typing import List, Dict, Any
from datetime import datetime
from app.domain.schemas import (
    VMCreateRequest,
    VMDTO,
    VMUpdateRequest,
    VMActionRequest,
    ProviderEnum,
    VMBuildRequest,
)
from app.domain.ports import VMRepositoryPort
from app.domain.factory_provider import create_cloud_factory, CloudProvider
from app.domain.abstractions.factory import CloudResourceManager
from app.infrastructure.logger import audit_log
from app.domain.builders import (
    VMTierDirector,
    VMBuilder,
    AWSVMBuilder,
    AzureVMBuilder,
    GCPVMBuilder,
    OnPremVMBuilder,
    OracleVMBuilder,
)


class VMService:
    def __init__(self, repo: VMRepositoryPort):
        self.repo = repo

    def _to_cloud_provider(self, provider: ProviderEnum) -> CloudProvider:
        value = provider.value if isinstance(provider, ProviderEnum) else str(provider)
        if value == "onpremise":
            return CloudProvider.ONPREM
        return CloudProvider(value)

    def create_vm(self, data: VMCreateRequest) -> VMDTO:
        # Usar el nuevo Abstract Factory
        try:
            provider = self._to_cloud_provider(data.provider)
            abstract_factory = create_cloud_factory(provider)

            # Crear VM usando Abstract Factory (firma: name, config)
            vm_config = data.params.model_dump()
            virtual_machine = abstract_factory.create_virtual_machine(data.name, vm_config)

            # Convertir a VMDTO
            vm = VMDTO(
                id=virtual_machine.resource_id,
                name=virtual_machine.name,
                provider=ProviderEnum(data.provider),
                status=virtual_machine.status.value,
                specs=virtual_machine.get_specs(),
            )
            
            self.repo.save(vm)
            audit_log(
                actor=data.requested_by or "system",
                action="create",
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details={"name": vm.name},
            )
            return vm
        except Exception as e:
            audit_log(
                actor=data.requested_by or "system",
                action="create",
                vm_id="",
                provider=data.provider,
                success=False,
                details={"error": str(e)},
            )
            raise

    def build_vm(self, data: VMBuildRequest) -> VMDTO:
        """
        Construye una VM con el patrón Builder+Director y la crea con la Abstract Factory.
        Director define CPU/RAM por tier; Builder traduce al esquema del proveedor.
        """
        try:
            # Elegir builder por proveedor
            builder: VMBuilder
            if data.provider == ProviderEnum.aws:
                builder = AWSVMBuilder()
            elif data.provider == ProviderEnum.azure:
                builder = AzureVMBuilder()
            elif data.provider == ProviderEnum.gcp:
                builder = GCPVMBuilder()
            elif data.provider == ProviderEnum.onpremise:
                builder = OnPremVMBuilder()
            elif data.provider == ProviderEnum.oracle:
                builder = OracleVMBuilder()
            else:
                raise ValueError(f"Proveedor no soportado: {data.provider}")

            director = VMTierDirector()
            vm_config = director.construct(
                builder,
                name=data.name,
                region=data.region,
                tier=data.tier.value,
                profile=data.profile,
                key_pair_name=data.key_pair_name,
                firewall_rules=data.firewall_rules,
                public_ip=data.public_ip,
                memory_optimization=data.memory_optimization,
                disk_optimization=data.disk_optimization,
                storage_iops=data.storage_iops,
            )

            # Crear con Abstract Factory
            provider_enum = self._to_cloud_provider(data.provider)
            factory = create_cloud_factory(provider_enum)
            vm = factory.create_virtual_machine(data.name, vm_config)

            dto = VMDTO(
                id=vm.resource_id,
                name=vm.name,
                provider=data.provider,
                status=vm.status.value,
                specs=vm.get_specs(),
            )
            self.repo.save(dto)
            audit_log(
                actor="system",
                action="create(builder)",
                vm_id=dto.id,
                provider=dto.provider,
                success=True,
                details={"tier": data.tier.value, "region": data.region},
            )
            return dto
        except Exception as e:
            audit_log(
                actor="system",
                action="create(builder)",
                vm_id="",
                provider=data.provider,
                success=False,
                details={"error": str(e)},
            )
            raise
    
    def create_infrastructure(
        self, 
        provider_name: str,
        infrastructure_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Nuevo método que utiliza el Abstract Factory para crear infraestructura completa.
        
        Args:
            provider_name: Nombre del proveedor (aws, azure, etc.)
            infrastructure_config: Configuración de la infraestructura completa
            
        Returns:
            Diccionario con la infraestructura creada
        """
        try:
            # Mapear a CloudProvider y obtener la factory
            prov = provider_name.lower()
            if prov == "onpremise":
                cp = CloudProvider.ONPREM
            else:
                cp = CloudProvider(prov)
            cloud_factory = create_cloud_factory(cp)
            
            # Crear el resource manager con la factory
            resource_manager = CloudResourceManager(cloud_factory)
            
            # Crear la infraestructura completa
            infrastructure = resource_manager.create_infrastructure(infrastructure_config)
            
            # Log de la operación exitosa
            audit_log(
                actor=infrastructure_config.get("requested_by", "system"),
                action="create_infrastructure",
                vm_id="multiple",
                provider=provider_name,
                success=True,
                details={
                    "resources_created": len(infrastructure),
                    "provider": cloud_factory.get_provider_name()
                }
            )
            
            return {
                "success": True,
                "infrastructure": infrastructure,
                "provider": cloud_factory.get_provider_name(),
                "resources_created": len(infrastructure)
            }
            
        except Exception as e:
            audit_log(
                actor=infrastructure_config.get("requested_by", "system"),
                action="create_infrastructure",
                vm_id="multiple",
                provider=provider_name,
                success=False,
                details={"error": str(e)}
            )
            raise

    def update_vm(self, vm_id: str, changes: VMUpdateRequest) -> VMDTO:
        vm = self.repo.get(vm_id)
        try:
            # Actualizar nombre si viene
            if changes.name is not None:
                vm.name = changes.name

            # Actualizar specs conocidas si vienen
            if vm.specs is None:
                vm.specs = {}
            if changes.cpu is not None:
                vm.specs["cpu"] = changes.cpu
            if changes.ram_gb is not None:
                vm.specs["ram_gb"] = changes.ram_gb
            if changes.disk_gb is not None:
                vm.specs["disk_gb"] = changes.disk_gb
            if changes.instance_type is not None:
                vm.specs["instance_type"] = changes.instance_type
            if changes.size is not None:
                vm.specs["vm_size"] = changes.size
            if changes.machine_type is not None:
                vm.specs["machine_type"] = changes.machine_type

            self.repo.save(vm)
            audit_log(
                actor="system",
                action="update",
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details=changes.model_dump(exclude_none=True),
            )
            return vm
        except Exception as e:
            audit_log(
                actor="system",
                action="update",
                vm_id=vm_id,
                provider=vm.provider if vm else "unknown",
                success=False,
                details={"error": str(e)},
            )
            raise

    def delete_vm(self, vm_id: str) -> None:
        vm = self.repo.get(vm_id)
        try:
            # No intentamos recrear la VM; simplemente eliminamos del repositorio
            self.repo.delete(vm_id)
            audit_log(
                actor="system",
                action="delete",
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details=None,
            )
        except Exception as e:
            audit_log(
                actor="system",
                action="delete",
                vm_id=vm_id,
                provider=vm.provider if vm else "unknown",
                success=False,
                details={"error": str(e)},
            )
            raise

    def apply_action(self, vm_id: str, action_req: VMActionRequest) -> VMDTO:
        vm = self.repo.get(vm_id)
        try:
            # Simular acciones actualizando el estado
            if action_req.action == "start":
                vm.status = "running"
            elif action_req.action == "stop":
                vm.status = "stopped"
            elif action_req.action == "restart":
                vm.status = "running"
            
            self.repo.save(vm)
            audit_log(
                actor=action_req.requested_by or "system",
                action=action_req.action,
                vm_id=vm.id,
                provider=vm.provider,
                success=True,
                details=None,
            )
            return vm
        except Exception as e:
            audit_log(
                actor=action_req.requested_by or "system",
                action=action_req.action,
                vm_id=vm_id,
                provider=vm.provider if vm else "unknown",
                success=False,
                details={"error": str(e)},
            )
            raise

    def get_vm(self, vm_id: str) -> VMDTO:
        return self.repo.get(vm_id)

    def list_vms(self) -> List[VMDTO]:
        return self.repo.list()