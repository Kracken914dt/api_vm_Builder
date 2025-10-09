
from __future__ import annotations
from typing import Dict, Any, List
import uuid
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class ComputeEngineInstance(VirtualMachine):
    """Implementación concreta de VM para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        self.zone = config.get("zone", "us-central1-a")
        self.machine_type = config.get("machine_type", "e2-standard-2")
        self.boot_disk_size = config.get("boot_disk_size", 20)
        self.project_id = config.get("project_id", "my-gcp-project")
        super().__init__(
            resource_id=f"gcp-vm-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-instance-{uuid.uuid4().hex[:6]}"),
            region=self.zone.split('-')[0] + '-' + self.zone.split('-')[1],
        )
        
    def start(self) -> None:
        """Iniciar la instancia de Compute Engine"""
        print(f"🟢 GCP: Iniciando Compute Engine instance {self.name} en zona {self.zone}")
        self.status = ResourceStatus.RUNNING
        
    def stop(self) -> None:
        """Detener la instancia de Compute Engine"""
        print(f"🔴 GCP: Deteniendo Compute Engine instance {self.name}")
        self.status = ResourceStatus.STOPPED
        
    def restart(self) -> None:
        print(f"🔁 GCP: Reiniciando Compute Engine instance {self.name}")
        self.status = ResourceStatus.RUNNING

    def resize(self, new_size: str) -> None:
        print(f"🔄 GCP: Cambiando machine type de {self.machine_type} a {new_size}")
        self.machine_type = new_size
        
    def get_resource_type(self) -> str:
        return "gcp.compute.instance"

    def get_specs(self) -> Dict[str, Any]:
        return {
            "zone": self.zone,
            "machine_type": self.machine_type,
            "boot_disk_size": self.boot_disk_size,
            "project_id": self.project_id
        }


class CloudSQLDatabase(Database):
    """Implementación concreta de base de datos para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        self.engine = config.get("engine", "postgres")
        self.engine_version = config.get("engine_version", "13")
        self.tier = config.get("tier", "db-standard-1")
        region = config.get("region", "us-central1")
        self.storage_size = config.get("storage_size", 20)
        super().__init__(
            resource_id=f"gcp-db-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-cloudsql-{uuid.uuid4().hex[:6]}"),
            region=region,
        )
        
    def backup(self) -> str:
        backup_id = f"backup-{uuid.uuid4().hex[:8]}"
        print(f"💾 GCP: Creando backup {backup_id} para Cloud SQL {self.name}")
        return backup_id

    def restore(self, backup_id: str) -> None:
        print(f"♻️ GCP: Restaurando Cloud SQL {self.name} desde backup {backup_id}")

    def scale(self, new_tier: str) -> None:
        print(f"📈 GCP: Escalando Cloud SQL {self.name} a tier {new_tier}")
        self.tier = new_tier

    def get_resource_type(self) -> str:
        return "gcp.cloudsql.instance"

    def get_specs(self) -> Dict[str, Any]:
        return {
            "engine": self.engine,
            "engine_version": self.engine_version,
            "tier": self.tier,
            "region": self.region,
            "storage_size": self.storage_size
        }


class CloudLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        self.load_balancer_type = config.get("type", "HTTP(S)")
        region = config.get("region", "us-central1")
        self.backend_services = config.get("backend_services", [])
        super().__init__(
            resource_id=f"gcp-lb-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-lb-{uuid.uuid4().hex[:6]}"),
            region=region,
        )
        
    def add_target(self, target_id: str) -> None:
        self.backend_services.append({"id": target_id})
        print(f"➕ GCP: Añadiendo target {target_id} al Load Balancer {self.name}")

    def remove_target(self, target_id: str) -> None:
        self.backend_services = [t for t in self.backend_services if t["id"] != target_id]
        print(f"➖ GCP: Removiendo target {target_id} del Load Balancer {self.name}")

    def configure_health_check(self, config: Dict[str, Any]) -> None:
        print(f"🔍 GCP: Configurando health check para Load Balancer {self.name}")

    def get_resource_type(self) -> str:
        return "gcp.loadbalancer"

    def get_specs(self) -> Dict[str, Any]:
        return {
            "type": self.load_balancer_type,
            "region": self.region,
            "backend_services": self.backend_services
        }


class CloudStorage(Storage):
    """Implementación concreta de almacenamiento para Google Cloud Platform"""
    
    def __init__(self, config: Dict[str, Any]):
        self.location = config.get("location", "US")
        self.storage_class = config.get("storage_class", "STANDARD")
        self.versioning_enabled = config.get("versioning_enabled", False)
        region = self.location if len(self.location) < 6 else "us-central1"
        super().__init__(
            resource_id=f"gcp-storage-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"gcp-bucket-{uuid.uuid4().hex[:6]}"),
            region=region,
        )
        
    def create_bucket(self, bucket_name: str) -> None:
        print(f"🪣 GCP: Creando bucket adicional {bucket_name} en {self.location}")

    def upload_file(self, file_path: str, key: str) -> None:
        print(f"⬆️ GCP: Subiendo {file_path} a gs://{self.name}/{key}")

    def download_file(self, key: str, local_path: str) -> None:
        print(f"⬇️ GCP: Descargando gs://{self.name}/{key} a {local_path}")

    def get_resource_type(self) -> str:
        return "gcp.storage.bucket"

    def get_specs(self) -> Dict[str, Any]:
        return {
            "location": self.location,
            "storage_class": self.storage_class,
            "versioning_enabled": self.versioning_enabled
        }