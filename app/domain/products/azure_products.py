"""
Productos concretos de Azure para el patrón Abstract Factory.
Estos implementan las interfaces abstractas para los servicios específicos de Azure.
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class AzureVirtualMachine(VirtualMachine):
    """Implementación concreta de VM para Azure"""
    
    def __init__(self, name: str, region: str, vm_size: str, image: str, resource_group: str):
        super().__init__(f"vm-{uuid.uuid4().hex[:8]}", name, region)
        self.vm_size = vm_size
        self.image = image
        self.resource_group = resource_group
        self.network_security_group: str = ""
        self.virtual_network: str = ""
        self.private_ip: str = ""
        self.public_ip: str = ""
    
    def get_resource_type(self) -> str:
        return "Microsoft.Compute/virtualMachines"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "vm_size": self.vm_size,
            "image": self.image,
            "resource_group": self.resource_group,
            "region": self.region,
            "network_security_group": self.network_security_group,
            "virtual_network": self.virtual_network,
            "private_ip": self.private_ip,
            "public_ip": self.public_ip
        }
    
    def start(self) -> None:
        """Inicia la VM de Azure"""
        if self.status == ResourceStatus.STOPPED:
            self.status = ResourceStatus.RUNNING
            print(f"✅ Azure VM {self.name} started in region {self.region}")
        else:
            raise ValueError(f"Cannot start VM in state {self.status}")
    
    def stop(self) -> None:
        """Detiene la VM de Azure"""
        if self.status == ResourceStatus.RUNNING:
            self.status = ResourceStatus.STOPPED
            print(f"⏹️ Azure VM {self.name} stopped")
        else:
            raise ValueError(f"Cannot stop VM in state {self.status}")
    
    def restart(self) -> None:
        """Reinicia la VM de Azure"""
        if self.status == ResourceStatus.RUNNING:
            print(f"🔄 Azure VM {self.name} restarting...")
            self.status = ResourceStatus.RUNNING
        else:
            raise ValueError(f"Cannot restart VM in state {self.status}")
    
    def resize(self, new_vm_size: str) -> None:
        """Cambia el tamaño de la VM"""
        old_size = self.vm_size
        self.vm_size = new_vm_size
        print(f"📏 Azure VM {self.name} resized from {old_size} to {new_vm_size}")


class AzureSQLDatabase(Database):
    """Implementación concreta de Database para Azure (SQL Database)"""
    
    def __init__(self, name: str, region: str, tier: str, server_name: str, resource_group: str):
        super().__init__(f"sqldb-{uuid.uuid4().hex[:8]}", name, region)
        self.tier = tier
        self.server_name = server_name
        self.resource_group = resource_group
        self.connection_string = f"Server={server_name}.database.windows.net;Database={name}"
        self.max_size_gb = 100
    
    def get_resource_type(self) -> str:
        return "Microsoft.Sql/servers/databases"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "tier": self.tier,
            "server_name": self.server_name,
            "resource_group": self.resource_group,
            "connection_string": self.connection_string,
            "max_size_gb": self.max_size_gb,
            "region": self.region
        }
    
    def backup(self) -> str:
        """Crea un backup de Azure SQL Database"""
        backup_id = f"backup-{uuid.uuid4().hex[:8]}"
        print(f"📋 Azure SQL Database {self.name} backup created: {backup_id}")
        return backup_id
    
    def restore(self, backup_id: str) -> None:
        """Restaura desde un backup"""
        print(f"🔄 Azure SQL Database {self.name} restored from backup: {backup_id}")
    
    def scale(self, new_tier: str) -> None:
        """Escala la base de datos"""
        old_tier = self.tier
        self.tier = new_tier
        print(f"📈 Azure SQL Database {self.name} scaled from {old_tier} to {new_tier}")


class AzureLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para Azure"""
    
    def __init__(self, name: str, region: str, resource_group: str, sku: str = "Standard"):
        super().__init__(f"lb-{uuid.uuid4().hex[:8]}", name, region)
        self.resource_group = resource_group
        self.sku = sku
        self.backend_pools: List[str] = []
        self.frontend_ip_configs: List[Dict[str, Any]] = []
        self.public_ip_address = f"{name}-ip-{self.resource_id[-8:]}"
    
    def get_resource_type(self) -> str:
        return "Microsoft.Network/loadBalancers"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "resource_group": self.resource_group,
            "sku": self.sku,
            "backend_pools": self.backend_pools,
            "frontend_ip_configs": self.frontend_ip_configs,
            "public_ip_address": self.public_ip_address,
            "region": self.region
        }
    
    def add_target(self, target_id: str) -> None:
        """Añade un target al backend pool"""
        if target_id not in self.backend_pools:
            self.backend_pools.append(target_id)
            print(f"🎯 Target {target_id} added to Azure Load Balancer {self.name}")
    
    def remove_target(self, target_id: str) -> None:
        """Remueve un target del backend pool"""
        if target_id in self.backend_pools:
            self.backend_pools.remove(target_id)
            print(f"❌ Target {target_id} removed from Azure Load Balancer {self.name}")
    
    def configure_health_check(self, config: Dict[str, Any]) -> None:
        """Configura health probes"""
        health_probe = {
            "protocol": config.get("protocol", "HTTP"),
            "port": config.get("port", 80),
            "path": config.get("path", "/"),
            "interval": config.get("interval", 15)
        }
        print(f"❤️ Health probe configured for Azure Load Balancer {self.name}: {health_probe}")


class AzureBlobStorage(Storage):
    """Implementación concreta de Storage para Azure (Blob Storage)"""
    
    def __init__(self, name: str, region: str, account_type: str = "Standard_LRS"):
        super().__init__(f"blob-{uuid.uuid4().hex[:8]}", name, region)
        self.storage_account_name = name
        self.account_type = account_type
        self.containers: Dict[str, Dict[str, Any]] = {}
        self.access_tier = "Hot"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={name};AccountKey=..."
    
    def get_resource_type(self) -> str:
        return "Microsoft.Storage/storageAccounts"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "storage_account_name": self.storage_account_name,
            "account_type": self.account_type,
            "access_tier": self.access_tier,
            "region": self.region,
            "container_count": len(self.containers),
            "connection_string": self.connection_string
        }
    
    def create_bucket(self, container_name: str) -> None:
        """Crea un contenedor en Blob Storage"""
        self.containers[container_name] = {"blobs": {}, "access_level": "private"}
        print(f"🪣 Azure Blob Container {container_name} created in storage account {self.storage_account_name}")
    
    def upload_file(self, file_path: str, blob_name: str, container: str = "default") -> None:
        """Simula la subida de un blob"""
        if container not in self.containers:
            self.create_bucket(container)
        
        self.containers[container]["blobs"][blob_name] = {
            "size": 1024,  # Simulado
            "last_modified": "2024-01-01T00:00:00Z",
            "access_tier": self.access_tier
        }
        print(f"⬆️ Blob uploaded to Azure Storage: {self.storage_account_name}/{container}/{blob_name}")
    
    def download_file(self, blob_name: str, local_path: str, container: str = "default") -> None:
        """Simula la descarga de un blob"""
        if container in self.containers and blob_name in self.containers[container]["blobs"]:
            print(f"⬇️ Blob downloaded from Azure Storage: {self.storage_account_name}/{container}/{blob_name} -> {local_path}")
        else:
            raise FileNotFoundError(f"Blob {blob_name} not found in container {container}")


class AzureNetworkInterface(NetworkInterface):
    """Implementación de interfaz de red para Azure VMs"""
    
    def __init__(self, vm_id: str):
        self.vm_id = vm_id
        self.network_security_groups: List[str] = []
        self.public_ip: str = ""
        self.virtual_network: str = ""
        self.subnet: str = ""
    
    def configure_security_group(self, rules: Dict[str, Any]) -> None:
        """Configura Network Security Groups"""
        nsg_id = f"nsg-{uuid.uuid4().hex[:8]}"
        self.network_security_groups.append(nsg_id)
        print(f"🔒 Network Security Group {nsg_id} configured for VM {self.vm_id}")
    
    def assign_public_ip(self) -> str:
        """Asigna una IP pública"""
        self.public_ip = f"40.{uuid.uuid4().int % 256}.{uuid.uuid4().int % 256}.{uuid.uuid4().int % 256}"
        print(f"🌐 Public IP {self.public_ip} assigned to VM {self.vm_id}")
        return self.public_ip