"""
Fábrica concreta de Azure que implementa el Abstract Factory.
Crea familias de productos específicos de Azure que trabajan juntos.
"""
from typing import Dict, Any
from ..abstractions.factory import CloudAbstractFactory
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage
from ..products.azure_products import AzureVirtualMachine, AzureSQLDatabase, AzureLoadBalancer, AzureBlobStorage


class AzureCloudFactory(CloudAbstractFactory):
    """
    Fábrica concreta para crear productos de Azure.
    Implementa el Abstract Factory pattern para Azure.
    """
    
    def __init__(self):
        self._supported_regions = {
            "eastus", "westus", "westus2", "northeurope", "westeurope",
            "southeastasia", "eastasia", "japaneast", "australiaeast"
        }
    
    def create_virtual_machine(self, name: str, vm_config: Dict[str, Any]) -> VirtualMachine:
        """Crea una VM de Azure"""
        required_fields = ["vm_size", "image", "resource_group", "region"]
        self._validate_config(vm_config, required_fields)
        
        region = vm_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by Azure")
        
        vm = AzureVirtualMachine(
            name=name,
            region=region,
            vm_size=vm_config["vm_size"],
            image=vm_config["image"],
            resource_group=vm_config["resource_group"]
        )
        
        # Configuraciones opcionales
        if "virtual_network" in vm_config:
            vm.virtual_network = vm_config["virtual_network"]
        if "network_security_group" in vm_config:
            vm.network_security_group = vm_config["network_security_group"]
        if vm_config.get("public_ip"):
            vm.public_ip = "40.0.0.1"  # simulado
        if "vcpus" in vm_config:
            vm.tags["vcpus"] = str(vm_config["vcpus"])
        if "memory_gb" in vm_config:
            vm.tags["memory_gb"] = str(vm_config["memory_gb"])
        
        print(f"🏭 Azure Factory: Created VM {name} ({vm_config['vm_size']})")
        return vm
    
    def create_database(self, name: str, db_config: Dict[str, Any]) -> Database:
        """Crea una Azure SQL Database"""
        required_fields = ["tier", "server_name", "resource_group", "region"]
        self._validate_config(db_config, required_fields)
        
        region = db_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by Azure")
        
        db = AzureSQLDatabase(
            name=name,
            region=region,
            tier=db_config["tier"],
            server_name=db_config["server_name"],
            resource_group=db_config["resource_group"]
        )
        
        if "max_size_gb" in db_config:
            db.max_size_gb = db_config["max_size_gb"]
        
        print(f"🏭 Azure Factory: Created SQL Database {name} ({db_config['tier']})")
        return db
    
    def create_load_balancer(self, name: str, lb_config: Dict[str, Any]) -> LoadBalancer:
        """Crea un Azure Load Balancer"""
        required_fields = ["resource_group", "region"]
        self._validate_config(lb_config, required_fields)
        
        region = lb_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by Azure")
        
        lb = AzureLoadBalancer(
            name=name,
            region=region,
            resource_group=lb_config["resource_group"],
            sku=lb_config.get("sku", "Standard")
        )
        
        # Configurar frontend IP si se especifica
        if "frontend_ip_configs" in lb_config:
            lb.frontend_ip_configs = lb_config["frontend_ip_configs"]
        
        print(f"🏭 Azure Factory: Created Load Balancer {name}")
        return lb
    
    def create_storage(self, name: str, storage_config: Dict[str, Any]) -> Storage:
        """Crea una cuenta de almacenamiento Azure Blob"""
        required_fields = ["region"]
        self._validate_config(storage_config, required_fields)
        
        region = storage_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by Azure")
        
        storage = AzureBlobStorage(
            name=name,
            region=region,
            account_type=storage_config.get("account_type", "Standard_LRS")
        )
        
        # Configurar access tier si se especifica
        if "access_tier" in storage_config:
            storage.access_tier = storage_config["access_tier"]
        
        print(f"🏭 Azure Factory: Created Blob Storage {name}")
        return storage
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna información completa sobre el proveedor Azure"""
        return {
            "name": "Microsoft Azure",
            "code": "azure",
            "supported_regions": self._supported_regions,
            "services": {
                "compute": "Virtual Machines",
                "database": "Azure SQL Database",
                "load_balancer": "Azure Load Balancer",
                "storage": "Blob Storage"
            }
        }
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "Microsoft Azure"
    
    def validate_region(self, region: str) -> bool:
        """Valida si la región es soportada por Azure"""
        return region in self._supported_regions
    
    def _validate_config(self, config: Dict[str, Any], required_fields: list) -> None:
        """Valida que la configuración tenga los campos requeridos"""
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(f"Missing required fields for Azure: {missing_fields}")
    
    def get_supported_regions(self) -> set:
        """Retorna las regiones soportadas"""
        return self._supported_regions.copy()
    
    def get_recommended_vm_sizes(self) -> Dict[str, list]:
        """Retorna tamaños de VM recomendados por caso de uso"""
        return {
            "general": ["Standard_B1s", "Standard_B2s", "Standard_D2s_v3"],
            "compute": ["Standard_F2s_v2", "Standard_F4s_v2", "Standard_F8s_v2"],
            "memory": ["Standard_E2s_v3", "Standard_E4s_v3", "Standard_E8s_v3"],
            "storage": ["Standard_L4s", "Standard_L8s", "Standard_L16s"]
        }