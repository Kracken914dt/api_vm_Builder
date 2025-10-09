"""
Productos concretos de Oracle Cloud para el patrón Abstract Factory.
Estos implementan las interfaces abstractas para los servicios específicos de Oracle Cloud Infrastructure (OCI).
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class OracleComputeInstance(VirtualMachine):
    """Implementación concreta de VM para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "us-ashburn-1")
        super().__init__(
            resource_id=f"oci-vm-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-instance-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.compute_shape = config.get("compute_shape", "VM.Standard2.1")
        self.availability_domain = config.get("availability_domain", "AD-1")
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.subnet_id = config.get("subnet_id", "ocid1.subnet.oc1..example")
        self.image_id = config.get("image_id", "ocid1.image.oc1..example")
        
    def start(self) -> None:
        print(f"🟢 Oracle: Iniciando Compute instance {self.name} en AD {self.availability_domain}")
        self.status = ResourceStatus.RUNNING
        
    def stop(self) -> None:
        print(f"🔴 Oracle: Deteniendo Compute instance {self.name}")
        self.status = ResourceStatus.STOPPED
        
    def restart(self) -> None:
        print(f"🔁 Oracle: Reiniciando Compute instance {self.name}")
        self.status = ResourceStatus.RUNNING
        
    def resize(self, new_size: str) -> None:
        print(f"🔄 Oracle: Cambiando shape de {self.compute_shape} a {new_size}")
        self.compute_shape = new_size
        
    def get_resource_type(self) -> str:
        return "oracle.compute.instance"
        
    def get_specs(self) -> Dict[str, Any]:
        return {
            "compute_shape": self.compute_shape,
            "availability_domain": self.availability_domain,
            "compartment_id": self.compartment_id,
            "subnet_id": self.subnet_id,
            "image_id": self.image_id
        }
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "compute_shape": self.compute_shape,
            "availability_domain": self.availability_domain,
            "compartment_id": self.compartment_id,
            "subnet_id": self.subnet_id,
            "image_id": self.image_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OracleAutonomousDatabase(Database):
    """Implementación concreta de base de datos para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "us-ashburn-1")
        super().__init__(
            resource_id=f"oci-db-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-adb-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.workload_type = config.get("workload_type", "OLTP")  # OLTP, DW, AJD, APEX
        self.cpu_count = config.get("cpu_count", 1)
        self.storage_tb = config.get("storage_tb", 1)
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.admin_password = config.get("admin_password", "SecurePass123!")
        
    def backup(self) -> str:
        backup_id = f"backup-{uuid.uuid4().hex[:8]}"
        print(f"💾 Oracle: Creando backup {backup_id} para Autonomous Database {self.name}")
        return backup_id
        
    def restore(self, backup_id: str) -> None:
        print(f"♻️ Oracle: Restaurando Autonomous Database {self.name} desde backup {backup_id}")
        
    def scale(self, new_tier: str) -> None:
        print(f"📈 Oracle: Escalando Autonomous Database {self.name} a tier {new_tier}")
        
    def get_resource_type(self) -> str:
        return "oracle.database.autonomous"
        
    def get_specs(self) -> Dict[str, Any]:
        return {
            "workload_type": self.workload_type,
            "cpu_count": self.cpu_count,
            "storage_tb": self.storage_tb,
            "compartment_id": self.compartment_id
        }
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "workload_type": self.workload_type,
            "cpu_count": self.cpu_count,
            "storage_tb": self.storage_tb,
            "compartment_id": self.compartment_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OracleLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "us-ashburn-1")
        super().__init__(
            resource_id=f"oci-lb-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-lb-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.shape = config.get("shape", "100Mbps")  # 10Mbps, 100Mbps, 400Mbps, 8000Mbps
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.subnet_ids = config.get("subnet_ids", [])
        self.backend_sets = []
        
    def add_target(self, target_id: str) -> None:
        target_info = {"id": target_id}
        self.backend_sets.append(target_info)
        print(f"➕ Oracle: Añadiendo backend {target_id} al Load Balancer {self.name}")
        
    def remove_target(self, target_id: str) -> None:
        self.backend_sets = [t for t in self.backend_sets if t["id"] != target_id]
        print(f"➖ Oracle: Removiendo backend {target_id} del Load Balancer {self.name}")
        
    def configure_health_check(self, config: Dict[str, Any]) -> None:
        print(f"🔍 Oracle: Configurando health check para Load Balancer {self.name}")
        
    def get_resource_type(self) -> str:
        return "oracle.loadbalancer"
        
    def get_specs(self) -> Dict[str, Any]:
        return {
            "shape": self.shape,
            "compartment_id": self.compartment_id,
            "subnet_ids": self.subnet_ids,
            "backend_sets": self.backend_sets
        }
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "shape": self.shape,
            "compartment_id": self.compartment_id,
            "subnet_ids": self.subnet_ids,
            "backend_sets": self.backend_sets,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OracleObjectStorage(Storage):
    """Implementación concreta de almacenamiento para Oracle Cloud Infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "us-ashburn-1")
        super().__init__(
            resource_id=f"oci-storage-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"oci-bucket-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.namespace = config.get("namespace", "my-namespace")
        self.compartment_id = config.get("compartment_id", "ocid1.compartment.oc1..example")
        self.storage_tier = config.get("storage_tier", "Standard")  # Standard, InfrequentAccess, Archive
        self.versioning_enabled = config.get("versioning_enabled", False)
        
    def create_bucket(self, bucket_name: str) -> None:
        print(f"🪣 Oracle: Creando bucket adicional {bucket_name} en namespace {self.namespace}")
        
    def upload_file(self, file_path: str, key: str) -> None:
        object_url = f"https://objectstorage.{self.namespace}.oraclecloud.com/n/{self.namespace}/b/{self.name}/o/{key}"
        print(f"⬆️ Oracle: Subiendo {file_path} a Object Storage como {object_url}")
        
    def download_file(self, key: str, local_path: str) -> None:
        print(f"⬇️ Oracle: Descargando {key} desde Object Storage bucket {self.name}")
        
    def get_resource_type(self) -> str:
        return "oracle.storage.bucket"
        
    def get_specs(self) -> Dict[str, Any]:
        return {
            "namespace": self.namespace,
            "compartment_id": self.compartment_id,
            "storage_tier": self.storage_tier,
            "versioning_enabled": self.versioning_enabled
        }
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "namespace": self.namespace,
            "compartment_id": self.compartment_id,
            "storage_tier": self.storage_tier,
            "versioning_enabled": self.versioning_enabled,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }