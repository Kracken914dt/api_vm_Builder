"""
Controlador para el patrón Abstract Factory.
Demuestra el uso del Abstract Factory para crear familias de productos de cloud.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.factory_provider import (
    create_cloud_factory,
    get_available_providers,
    CloudProvider
)
from app.domain.abstractions.factory import CloudResourceManager
from app.core.container import get_vm_service
from app.domain.services import VMService
from app.infrastructure.logger import audit_log

router = APIRouter()


class InfrastructureCreateRequest(BaseModel):
    """Request model para crear infraestructura completa"""
    provider: str = Field(..., description="Proveedor de cloud (aws, azure, gcp, oracle, onprem)")
    name: str = Field(..., description="Nombre de la infraestructura")
    region: Optional[str] = Field("us-east-1", description="Región donde crear la infraestructura")
    vm_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de VM")
    database_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de base de datos") 
    load_balancer_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de load balancer")
    storage_config: Optional[Dict[str, Any]] = Field(None, description="Configuración de almacenamiento")
    include_database: Optional[bool] = Field(True, description="Incluir base de datos")
    include_load_balancer: Optional[bool] = Field(True, description="Incluir load balancer")
    include_storage: Optional[bool] = Field(True, description="Incluir almacenamiento")
    requested_by: Optional[str] = Field("system", description="Usuario que solicita la creación")

    class Config:
        schema_extra = {
            "example": {
                "provider": "aws",
                "vm": {
                    "name": "web-server-vm",
                    "config": {
                        "instance_type": "t3.micro",
                        "ami": "ami-0abcdef1234567890",
                        "vpc_id": "vpc-12345",
                        "region": "us-east-1"
                    }
                },
                "database": {
                    "name": "app-database",
                    "config": {
                        "engine": "mysql",
                        "instance_class": "db.t3.micro",
                        "allocated_storage": 20,
                        "region": "us-east-1"
                    }
                },
                "load_balancer": {
                    "name": "web-lb",
                    "config": {
                        "vpc_id": "vpc-12345",
                        "region": "us-east-1",
                        "scheme": "internet-facing"
                    }
                },
                "storage": {
                    "name": "app-storage-bucket",
                    "config": {
                        "region": "us-east-1",
                        "storage_class": "STANDARD"
                    }
                },
                "requested_by": "admin"
            }
        }


class InfrastructureResponse(BaseModel):
    """Response model para operaciones de infraestructura"""
    success: bool
    message: str
    provider: Optional[str] = None
    infrastructure_id: Optional[str] = None
    resources_created: Optional[int] = None
    infrastructure: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class InfrastructureRecord(BaseModel):
    """Registro persistido en memoria de una infraestructura creada"""
    id: str
    name: str
    provider: str
    region: str
    created_at: datetime
    updated_at: datetime
    requested_by: str
    resources: Dict[str, Any]
    includes: Dict[str, bool]
    status: str = "active"  # active | deleted


class InfrastructureUpdateRequest(BaseModel):
    """Modelo para actualizar componentes de una infraestructura existente"""
    vm_config: Optional[Dict[str, Any]] = None
    database_config: Optional[Dict[str, Any]] = None
    load_balancer_config: Optional[Dict[str, Any]] = None
    storage_config: Optional[Dict[str, Any]] = None
    include_database: Optional[bool] = None
    include_load_balancer: Optional[bool] = None
    include_storage: Optional[bool] = None
    requested_by: Optional[str] = "system"


class InfrastructureListResponse(BaseModel):
    """Listado de infraestructuras"""
    total: int
    items: List[InfrastructureRecord]


class InfrastructureDeleteResponse(BaseModel):
    success: bool
    message: str
    infrastructure_id: str


# Repositorio en memoria (simple singleton en este módulo)
class _InfrastructureRepository:
    def __init__(self):
        self._store: Dict[str, InfrastructureRecord] = {}

    def add(self, record: InfrastructureRecord):
        self._store[record.id] = record

    def list(self) -> List[InfrastructureRecord]:
        return [r for r in self._store.values() if r.status == "active"]

    def get(self, infra_id: str) -> Optional[InfrastructureRecord]:
        return self._store.get(infra_id)

    def update(self, infra_id: str, updater) -> InfrastructureRecord:
        rec = self._store.get(infra_id)
        if not rec or rec.status != "active":
            raise KeyError("Infraestructura no encontrada")
        updater(rec)
        rec.updated_at = datetime.utcnow()
        self._store[infra_id] = rec
        return rec

    def delete(self, infra_id: str) -> InfrastructureRecord:
        rec = self._store.get(infra_id)
        if not rec or rec.status != "active":
            raise KeyError("Infraestructura no encontrada")
        rec.status = "deleted"
        rec.updated_at = datetime.utcnow()
        return rec


_infra_repo = _InfrastructureRepository()


@router.post("/infrastructure/create", response_model=InfrastructureResponse)
def create_infrastructure(request: InfrastructureCreateRequest):
    """
    Crea una infraestructura completa usando el patrón Abstract Factory.
    
    Este endpoint demuestra cómo el Abstract Factory permite crear
    familias de productos relacionados de diferentes proveedores de cloud.
    """
    try:
        print(f"📦 Iniciando creación de infraestructura para proveedor: {request.provider}")
        
        # Obtener la factory para el proveedor
        try:
            provider_enum = CloudProvider(request.provider.lower())
            factory = create_cloud_factory(provider_enum)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Proveedor '{request.provider}' no soportado. Proveedores disponibles: {[p.value for p in CloudProvider]}"
            )
        print(f"🏭 Factory obtenida: {type(factory).__name__}")
        
        # Lista para almacenar recursos creados
        resources_created = []
        infrastructure_details = {}
        
        # Crear VM siempre (recurso base)
        vm_name = f"{request.name}-vm"
        
        # Preparar configuración de VM
        if request.vm_config:
            vm_config = request.vm_config.copy()
        else:
            vm_config = {}
        
        # Asegurar configuración mínima por proveedor
        vm_config["region"] = vm_config.get("region", request.region)
        
        if request.provider == "aws":
            # Campos requeridos por AWS factory - siempre necesarios
            if "instance_type" not in vm_config:
                vm_config["instance_type"] = "t2.micro"
            if "ami" not in vm_config:
                vm_config["ami"] = "ami-0abcdef1234567890"  
            if "vpc_id" not in vm_config:
                vm_config["vpc_id"] = "vpc-12345678"
            # Los campos opcionales como key_pair se preservan si los envió el usuario
        elif request.provider == "azure":
            vm_config.setdefault("vm_size", "Standard_B1s")
            vm_config.setdefault("resource_group", "rg-default")
            vm_config.setdefault("image", "Ubuntu 20.04 LTS")
        elif request.provider == "gcp":
            vm_config.setdefault("machine_type", "e2-micro")
            vm_config.setdefault("zone", "us-central1-a")
            vm_config.setdefault("project", "demo-project")
        elif request.provider == "oracle":
            vm_config.setdefault("compute_shape", "VM.Standard2.1")
            vm_config.setdefault("compartment_id", "ocid1.compartment.oc1..exampleuniqueID")
            vm_config.setdefault("availability_domain", "AD-1")
            vm_config.setdefault("subnet_id", "ocid1.subnet.oc1..examplesubnet")
            vm_config.setdefault("image_id", "ocid1.image.oc1..exampleimage")
        elif request.provider == "onprem":
            vm_config.setdefault("cpu", 2)
            vm_config.setdefault("ram_gb", 4)
            vm_config.setdefault("disk_gb", 50)
        
        vm = factory.create_virtual_machine(vm_name, vm_config)
        vm_info = {
            "name": vm.name,
            "resource_id": vm.resource_id,
            "region": vm.region,
            "status": vm.status.value,
            "type": vm.get_resource_type(),
            "specs": vm.get_specs()
        }
        resources_created.append("virtual_machine")
        infrastructure_details["virtual_machine"] = vm_info
        print(f"🖥️ VM creada: {vm_info}")
        
        # Crear Database si se requiere
        if request.include_database:
            db_name = f"{request.name}-db"
            if request.provider == "azure":
                # Defaults específicos de Azure (campos requeridos: tier, server_name, resource_group, region)
                if request.database_config:
                    db_config = request.database_config.copy()
                else:
                    db_config = {
                        "region": request.region,
                        "tier": "Basic",
                        "server_name": f"{request.name}-sqlsrv",
                        "resource_group": vm_config.get("resource_group", "rg-default")
                    }
                # Asegurar campos faltantes mínimos
                db_config.setdefault("tier", "Basic")
                db_config.setdefault("server_name", f"{request.name}-sqlsrv")
                db_config.setdefault("resource_group", vm_config.get("resource_group", "rg-default"))
                db_config.setdefault("region", request.region)
            elif request.provider == "oracle":
                # Defaults específicos de Oracle
                db_config = request.database_config or {}
                db_config.setdefault("workload_type", "OLTP")
                db_config.setdefault("compartment_id", vm_config.get("compartment_id", "ocid1.compartment.oc1..exampleuniqueID"))
                db_config.setdefault("cpu_count", 1)
                db_config.setdefault("storage_size", 20)
                db_config.setdefault("region", request.region)
            else:
                # Defaults genéricos (ej. AWS, GCP, OnPrem, etc.)
                db_config = request.database_config or {
                    "region": request.region,
                    "engine": "mysql",
                    "instance_class": "db.t3.micro",
                    "allocated_storage": 20
                }
            
            db = factory.create_database(db_name, db_config)
            db_info = {
                "name": db.name,
                "resource_id": db.resource_id,
                "region": db.region,
                "status": db.status.value,
                "type": db.get_resource_type(),
                "specs": db.get_specs()
            }
            resources_created.append("database")
            infrastructure_details["database"] = db_info
            print(f"🗄️ Database creada: {db_info}")
        
        # Crear Load Balancer si se requiere
        if request.include_load_balancer:
            lb_name = f"{request.name}-lb"
            lb_config = request.load_balancer_config or {
                "region": request.region,
                "load_balancer_type": "application",
                "scheme": "internet-facing"
            }
            
            # Asegurar campos requeridos por proveedor para Load Balancer
            if request.provider == "aws":
                if "vpc_id" not in lb_config:
                    lb_config["vpc_id"] = "vpc-12345678"  # Usar el mismo VPC que la VM
            elif request.provider == "azure":
                # Azure requiere resource_group y region
                lb_config.setdefault("resource_group", vm_config.get("resource_group", "rg-default"))
            elif request.provider == "oracle":
                # Oracle requiere compartment_id
                lb_config.setdefault("compartment_id", vm_config.get("compartment_id", "ocid1.compartment.oc1..exampleuniqueID"))
                lb_config.setdefault("shape", "100Mbps")
            
            lb = factory.create_load_balancer(lb_name, lb_config)
            lb_info = {
                "name": lb.name,
                "resource_id": lb.resource_id,
                "region": lb.region,
                "status": lb.status.value,
                "type": lb.get_resource_type(),
                "specs": lb.get_specs()
            }
            resources_created.append("load_balancer")
            infrastructure_details["load_balancer"] = lb_info
            print(f"⚖️ Load Balancer creado: {lb_info}")
        
        # Crear Storage si se requiere
        if request.include_storage:
            storage_name = f"{request.name}-storage"
            
            # Defaults específicos por proveedor para storage
            if request.storage_config:
                storage_config = request.storage_config
            else:
                if request.provider == "aws":
                    storage_config = {
                        "region": request.region,
                        "size_gb": 100,
                        "storage_type": "gp3"
                    }
                elif request.provider == "onprem":
                    storage_config = {
                        "region": request.region,
                        "storage_type": "nfs",
                        "capacity_gb": 1000
                    }
                elif request.provider == "oracle":
                    storage_config = {
                        "region": request.region,
                        "namespace": "mytenantns",
                        "compartment_id": vm_config.get("compartment_id", "ocid1.compartment.oc1..exampleuniqueID"),
                        "storage_tier": "Standard"
                    }
                else:
                    storage_config = {
                        "region": request.region,
                        "size_gb": 100,
                        "storage_type": "standard"
                    }
            
            storage = factory.create_storage(storage_name, storage_config) 
            storage_info = {
                "name": storage.name,
                "resource_id": storage.resource_id,
                "region": storage.region,
                "status": storage.status.value,
                "type": storage.get_resource_type(),
                "specs": storage.get_specs()
            }
            resources_created.append("storage")
            infrastructure_details["storage"] = storage_info
            print(f"💾 Storage creado: {storage_info}")
        
        # Registrar en logs
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id=f"{request.name}-infrastructure",
            provider=request.provider,
            success=True,
            details={
                "infrastructure_name": request.name,
                "resources_created": len(resources_created),
                "pattern": "Abstract Factory"
            }
        )
        
        infra_id = str(uuid4())
        record = InfrastructureRecord(
            id=infra_id,
            name=request.name,
            provider=request.provider,
            region=request.region,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            requested_by=request.requested_by,
            resources=infrastructure_details,
            includes={
                "database": request.include_database,
                "load_balancer": request.include_load_balancer,
                "storage": request.include_storage
            }
        )
        _infra_repo.add(record)

        result = InfrastructureResponse(
            success=True,
            message=f"Infraestructura '{request.name}' creada exitosamente usando {request.provider.upper()}",
            provider=request.provider,
            infrastructure_id=infra_id,
            resources_created=len(resources_created),
            infrastructure=infrastructure_details
        )
        
        print(f"✅ Infraestructura creada exitosamente: {len(resources_created)} recursos")
        return result
        
    except HTTPException as he:
        # Dejar pasar los errores ya formateados
        raise he
    except KeyError as e:
        error_msg = f"Proveedor '{request.provider}' no soportado. Proveedores disponibles: aws, azure, gcp, oracle, onprem"
        print(f"❌ Error de proveedor: {error_msg}")
        
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id="error",
            provider=request.provider,
            success=False,
            details={"error": "unsupported_provider"}
        )
        
        raise HTTPException(status_code=400, detail=error_msg)
        
    except Exception as e:
        error_msg = f"Error interno al crear infraestructura: {str(e)}"
        print(f"❌ Error interno: {error_msg}")
        
        audit_log(
            actor=request.requested_by,
            action="create_infrastructure",
            vm_id="error",
            provider=request.provider,
            success=False,
            details={"error": "internal_error", "details": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/providers", response_model=Dict[str, Any])
def get_supported_providers():
    """
    Obtiene la lista de proveedores de cloud soportados.
    """
    try:
        providers = get_available_providers()
        
        return {
            "supported_providers": providers,
            "total": len(providers),
            "description": "List of cloud providers supported by the Abstract Factory"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching providers")


@router.get("/providers/{provider}/info", response_model=Dict[str, Any])
def get_provider_info(provider: str):
    """
    Obtiene información específica de un proveedor.
    """
    try:
        # Convertir string a enum
        try:
            provider_enum = CloudProvider(provider.lower())
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Proveedor '{provider}' no soportado")

        factory = create_cloud_factory(provider_enum)
        
        info = {
            "provider_name": factory.get_provider_name(),
            "provider_code": provider,
            "supported_services": [
                "Virtual Machines",
                "Databases", 
                "Load Balancers",
                "Storage"
            ]
        }
        
        # Información específica por proveedor
        if hasattr(factory, 'get_supported_regions'):
            info["supported_regions"] = list(factory.get_supported_regions())
        
        if hasattr(factory, 'get_recommended_instance_types'):
            info["recommended_instance_types"] = factory.get_recommended_instance_types()
        elif hasattr(factory, 'get_recommended_vm_sizes'):
            info["recommended_vm_sizes"] = factory.get_recommended_vm_sizes()

        # Información específica adicional por proveedor
        # AWS ya expone recommended_instance_types
        if provider_enum == CloudProvider.GCP:
            if hasattr(factory, 'get_supported_machine_types'):
                info["machine_types"] = factory.get_supported_machine_types()
            if hasattr(factory, 'get_supported_database_engines'):
                info["database_engines"] = factory.get_supported_database_engines()
            if hasattr(factory, 'get_supported_load_balancer_types'):
                info["load_balancer_types"] = factory.get_supported_load_balancer_types()
            if hasattr(factory, 'get_supported_storage_classes'):
                info["storage_classes"] = factory.get_supported_storage_classes()
            if hasattr(factory, 'get_supported_locations'):
                info["locations"] = factory.get_supported_locations()
        elif provider_enum == CloudProvider.ORACLE:
            if hasattr(factory, 'get_supported_compute_shapes'):
                info["compute_shapes"] = factory.get_supported_compute_shapes()
            if hasattr(factory, 'get_supported_database_workloads'):
                info["database_workloads"] = factory.get_supported_database_workloads()
            if hasattr(factory, 'get_supported_load_balancer_shapes'):
                info["load_balancer_shapes"] = factory.get_supported_load_balancer_shapes()
            if hasattr(factory, 'get_supported_storage_tiers'):
                info["storage_tiers"] = factory.get_supported_storage_tiers()
        
        return info
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching provider info")


# ===================== NUEVOS ENDPOINTS CRUD INFRAESTRUCTURA =====================

@router.get("/infrastructure", response_model=InfrastructureListResponse)
def list_infrastructures():
    items = _infra_repo.list()
    return InfrastructureListResponse(total=len(items), items=items)


@router.get("/infrastructure/{infrastructure_id}", response_model=InfrastructureRecord)
def get_infrastructure(infrastructure_id: str):
    rec = _infra_repo.get(infrastructure_id)
    if not rec or rec.status != "active":
        raise HTTPException(status_code=404, detail="Infraestructura no encontrada")
    return rec


@router.put("/infrastructure/{infrastructure_id}", response_model=InfrastructureRecord)
def update_infrastructure(infrastructure_id: str, update: InfrastructureUpdateRequest):
    try:
        def _apply(rec: InfrastructureRecord):
            # Actualizar recursos existentes según configs nuevas
            if update.vm_config and "virtual_machine" in rec.resources:
                # Merge specs
                rec.resources["virtual_machine"]["specs"].update(update.vm_config)
            if update.database_config:
                if "database" in rec.resources:
                    rec.resources["database"]["specs"].update(update.database_config)
                else:
                    rec.includes["database"] = True
                    rec.resources["database"] = {"added": True, "specs": update.database_config}
            if update.load_balancer_config:
                if "load_balancer" in rec.resources:
                    rec.resources["load_balancer"]["specs"].update(update.load_balancer_config)
                else:
                    rec.includes["load_balancer"] = True
                    rec.resources["load_balancer"] = {"added": True, "specs": update.load_balancer_config}
            if update.storage_config:
                if "storage" in rec.resources:
                    rec.resources["storage"]["specs"].update(update.storage_config)
                else:
                    rec.includes["storage"] = True
                    rec.resources["storage"] = {"added": True, "specs": update.storage_config}
            # Flags de inclusión
            if update.include_database is not None:
                rec.includes["database"] = update.include_database
            if update.include_load_balancer is not None:
                rec.includes["load_balancer"] = update.include_load_balancer
            if update.include_storage is not None:
                rec.includes["storage"] = update.include_storage
        updated = _infra_repo.update(infrastructure_id, _apply)
        return updated
    except KeyError:
        raise HTTPException(status_code=404, detail="Infraestructura no encontrada")


@router.delete("/infrastructure/{infrastructure_id}", response_model=InfrastructureDeleteResponse)
def delete_infrastructure(infrastructure_id: str):
    try:
        rec = _infra_repo.delete(infrastructure_id)
        return InfrastructureDeleteResponse(
            success=True,
            message=f"Infraestructura '{rec.name}' eliminada (soft-delete)",
            infrastructure_id=infrastructure_id
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Infraestructura no encontrada")


@router.get("/infrastructure/examples", response_model=Dict[str, Any])
def get_infrastructure_examples():
    """
    Obtiene ejemplos de configuración de infraestructura para diferentes proveedores.
    """
    examples = {
        "aws": {
            "provider": "aws",
            "vm": {
                "name": "web-server",
                "config": {
                    "instance_type": "t3.micro",
                    "ami": "ami-0abcdef1234567890",
                    "vpc_id": "vpc-12345",
                    "region": "us-east-1",
                    "security_groups": ["sg-web-servers"]
                }
            },
            "database": {
                "name": "app-db",
                "config": {
                    "engine": "mysql",
                    "instance_class": "db.t3.micro",
                    "allocated_storage": 20,
                    "region": "us-east-1"
                }
            },
            "storage": {
                "name": "app-files",
                "config": {
                    "region": "us-east-1",
                    "storage_class": "STANDARD",
                    "versioning_enabled": True
                }
            }
        },
        "azure": {
            "provider": "azure",
            "vm": {
                "name": "web-server",
                "config": {
                    "vm_size": "Standard_B1s",
                    "image": "UbuntuLTS",
                    "resource_group": "my-rg",
                    "region": "eastus"
                }
            },
            "database": {
                "name": "app-db",
                "config": {
                    "tier": "Basic",
                    "server_name": "mydbserver",
                    "resource_group": "my-rg",
                    "region": "eastus"
                }
            },
            "storage": {
                "name": "appfiles",
                "config": {
                    "region": "eastus",
                    "account_type": "Standard_LRS",
                    "access_tier": "Hot"
                }
            }
        }
    }
    
    return {
        "description": "Example configurations for different cloud providers",
        "examples": examples
    }