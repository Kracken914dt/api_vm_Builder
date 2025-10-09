from typing import Dict, Any
from ..abstractions.factory import CloudAbstractFactory
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage
from ..products.onprem_products import OnPremiseVirtualMachine, OnPremiseDatabase, OnPremiseLoadBalancer, OnPremiseStorage


class OnPremiseCloudFactory(CloudAbstractFactory):

    def __init__(self):
        self.provider_name = "onprem"
        self.supported_hypervisors = ["vmware", "hyperv", "kvm", "xen"]
        self.supported_database_engines = ["postgresql", "mysql", "oracle", "sqlserver"]
        self.supported_load_balancer_types = ["nginx", "haproxy", "f5", "citrix"]
        self.supported_storage_types = ["nfs", "smb", "iscsi", "fc"]
    
    def create_virtual_machine(self, name: str, vm_config: Dict[str, Any]) -> VirtualMachine:
        config = vm_config.copy()
        config["name"] = name
        self._validate_vm_config(config)
        vm = OnPremiseVirtualMachine(config)
        print(f"🏭 OnPrem Factory: Creando VM {vm.name} en {vm.hypervisor}")
        return vm

    def create_database(self, name: str, db_config: Dict[str, Any]) -> Database:
        config = db_config.copy()
        config["name"] = name
        self._validate_database_config(config)
        database = OnPremiseDatabase(config)
        print(f"🏭 OnPrem Factory: Creando base de datos {database.name} ({database.engine})")
        return database

    def create_load_balancer(self, name: str, lb_config: Dict[str, Any]) -> LoadBalancer:
        config = lb_config.copy()
        config["name"] = name
        self._validate_load_balancer_config(config)
        load_balancer = OnPremiseLoadBalancer(config)
        print(f"🏭 OnPrem Factory: Creando Load Balancer {load_balancer.name} ({load_balancer.load_balancer_type})")
        return load_balancer

    def create_storage(self, name: str, storage_config: Dict[str, Any]) -> Storage:
        config = storage_config.copy()
        config["name"] = name
        self._validate_storage_config(config)
        storage = OnPremiseStorage(config)
        print(f"🏭 OnPrem Factory: Creando storage {storage.name} ({storage.storage_type})")
        return storage
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna información sobre el proveedor on-premise"""
        return {
            "name": "On-Premise Infrastructure",
            "code": "onprem",
            "supported_hypervisors": self.supported_hypervisors,
            "supported_database_engines": self.supported_database_engines,
            "supported_load_balancer_types": self.supported_load_balancer_types,
            "supported_storage_types": self.supported_storage_types,
            "services": {
                "compute": "Virtual Machines (VMware/Hyper-V/KVM/Xen)",
                "database": "Database Servers (PostgreSQL/MySQL/Oracle/SQL Server)",
                "load_balancer": "Load Balancers (Nginx/HAProxy/F5/Citrix)",
                "storage": "Network Storage (NFS/SMB/iSCSI/FC)"
            }
        }
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "On-Premise Infrastructure"
    
    def validate_region(self, region: str) -> bool:
        """Para on-premise, todas las 'regiones' (ubicaciones) son válidas"""
        return True
    
    def _validate_vm_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de VM on-premise"""
        required_fields = ["cpu", "ram_gb", "disk_gb", "nic"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para OnPrem VM: {field}")
        
        # Validar hipervisor válido
        hypervisor = config.get("hypervisor", "vmware")
        if hypervisor not in self.supported_hypervisors:
            raise ValueError(f"Hipervisor inválido para OnPrem: {hypervisor}. Soportados: {self.supported_hypervisors}")
        
        # Validar recursos mínimos
        if config["cpu"] < 1:
            raise ValueError("CPU mínimo: 1 core")
        if config["ram_gb"] < 1:
            raise ValueError("RAM mínima: 1GB")
        if config["disk_gb"] < 10:
            raise ValueError("Disco mínimo: 10GB")
    
    def _validate_database_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de base de datos on-premise"""
        required_fields = ["engine"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para OnPrem Database: {field}")
        
        # Validar engine soportado
        if config["engine"] not in self.supported_database_engines:
            raise ValueError(f"Engine de base de datos inválido para OnPrem: {config['engine']}. Soportados: {self.supported_database_engines}")
        
        # Validar puerto según engine
        default_ports = {
            "postgresql": 5432,
            "mysql": 3306,
            "oracle": 1521,
            "sqlserver": 1433
        }
        
        expected_port = default_ports.get(config["engine"])
        actual_port = config.get("port", expected_port)
        
        if actual_port != expected_port:
            print(f"⚠️ Advertencia: Puerto {actual_port} no es el estándar para {config['engine']} ({expected_port})")
    
    def _validate_load_balancer_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica del Load Balancer on-premise"""
        # Validar tipo de load balancer
        lb_type = config.get("type", "nginx")
        if lb_type not in self.supported_load_balancer_types:
            raise ValueError(f"Tipo de load balancer inválido para OnPrem: {lb_type}. Soportados: {self.supported_load_balancer_types}")
        
        # Validar algoritmo de balanceo
        valid_algorithms = ["round_robin", "least_conn", "ip_hash", "least_time"]
        algorithm = config.get("algorithm", "round_robin")
        if algorithm not in valid_algorithms:
            raise ValueError(f"Algoritmo de balanceo inválido: {algorithm}. Válidos: {valid_algorithms}")
    
    def _validate_storage_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de almacenamiento on-premise"""
        required_fields = ["storage_type"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para OnPrem Storage: {field}")
        
        # Validar tipo de almacenamiento soportado
        if config["storage_type"] not in self.supported_storage_types:
            raise ValueError(f"Tipo de storage inválido para OnPrem: {config['storage_type']}. Soportados: {self.supported_storage_types}")
        
        # Validar capacidad mínima
        capacity = config.get("capacity_gb", 100)
        if capacity < 10:
            raise ValueError("Capacidad mínima de storage: 10GB")