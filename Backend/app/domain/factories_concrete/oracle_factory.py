
from typing import Dict, Any
from ..abstractions.factory import CloudAbstractFactory
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage
from ..products.oracle_products import OracleComputeInstance, OracleAutonomousDatabase, OracleLoadBalancer, OracleObjectStorage


class OracleCloudFactory(CloudAbstractFactory):
    """
    Fábrica concreta para crear productos de Oracle Cloud Infrastructure.
    Implementa el Abstract Factory pattern para Oracle Cloud.
    """
    
    def __init__(self):
        self.provider_name = "oracle"
        self.supported_regions = [
            "us-ashburn-1", "us-phoenix-1", "us-sanjose-1",
            "ca-toronto-1", "ca-montreal-1",
            "eu-frankfurt-1", "eu-zurich-1", "eu-amsterdam-1",
            "uk-london-1", "ap-tokyo-1", "ap-osaka-1",
            "ap-sydney-1", "ap-melbourne-1", "ap-mumbai-1"
        ]
    
    def create_virtual_machine(self, name: str, vm_config: Dict[str, Any]) -> VirtualMachine:
        """
        Crea una instancia de Oracle Compute con la configuración especificada.
        
        Args:
            config: Configuración de la VM incluyendo compute_shape, availability_domain, etc.
            
        Returns:
            OracleComputeInstance: Nueva instancia de VM de Oracle Cloud
        """
        # Validar configuración específica de Oracle
        config = vm_config.copy()
        config["name"] = name
        self._validate_vm_config(config)
        
        # Crear la instancia de Oracle Compute
        vm = OracleComputeInstance(config)
        print(f"🏭 Oracle Factory: Creando Compute instance {vm.name}")
        
        return vm
    
    def create_database(self, name: str, db_config: Dict[str, Any]) -> Database:
        """
        Crea una Autonomous Database de Oracle con la configuración especificada.
        
        Args:
            config: Configuración de la base de datos incluyendo workload_type, cpu_count, etc.
            
        Returns:
            OracleAutonomousDatabase: Nueva instancia de base de datos de Oracle Cloud
        """
        # Validar configuración específica de Oracle
        config = db_config.copy()
        config["name"] = name
        self._validate_database_config(config)
        
        # Crear la Autonomous Database
        database = OracleAutonomousDatabase(config)
        print(f"🏭 Oracle Factory: Creando Autonomous Database {database.name}")
        
        return database
    
    def create_load_balancer(self, name: str, lb_config: Dict[str, Any]) -> LoadBalancer:
        """
        Crea un Load Balancer de Oracle Cloud con la configuración especificada.
        
        Args:
            config: Configuración del load balancer incluyendo shape, compartment_id, etc.
            
        Returns:
            OracleLoadBalancer: Nueva instancia de load balancer de Oracle Cloud
        """
        # Validar configuración específica de Oracle
        config = lb_config.copy()
        config["name"] = name
        self._validate_load_balancer_config(config)
        
        # Crear el Load Balancer
        load_balancer = OracleLoadBalancer(config)
        print(f"🏭 Oracle Factory: Creando Load Balancer {load_balancer.name}")
        
        return load_balancer
    
    def create_storage(self, name: str, storage_config: Dict[str, Any]) -> Storage:
        """
        Crea un bucket de Object Storage de Oracle con la configuración especificada.
        
        Args:
            config: Configuración del storage incluyendo namespace, compartment_id, etc.
            
        Returns:
            OracleObjectStorage: Nueva instancia de storage de Oracle Cloud
        """
        # Validar configuración específica de Oracle
        config = storage_config.copy()
        config["name"] = name
        self._validate_storage_config(config)
        
        # Crear el Object Storage bucket
        storage = OracleObjectStorage(config)
        print(f"🏭 Oracle Factory: Creando Object Storage bucket {storage.name}")
        
        return storage
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna información sobre el proveedor Oracle Cloud"""
        return {
            "name": "Oracle Cloud Infrastructure",
            "code": "oracle",
            "supported_regions": self.supported_regions,
            "services": {
                "compute": "Oracle Compute",
                "database": "Autonomous Database",
                "load_balancer": "Oracle Load Balancer",
                "storage": "Object Storage"
            }
        }
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "Oracle Cloud Infrastructure"
    
    def validate_region(self, region: str) -> bool:
        """Valida si la región es soportada por Oracle"""
        return region in self.supported_regions
    
    def _validate_vm_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de Oracle Compute"""
        required_fields = ["compute_shape", "compartment_id", "availability_domain", "subnet_id", "image_id"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para Oracle VM: {field}")
        
        # Validar compute shapes válidos de Oracle
        valid_compute_shapes = [
            "VM.Standard2.1", "VM.Standard2.2", "VM.Standard2.4", "VM.Standard2.8",
            "VM.Standard3.Flex", "VM.Optimized3.Flex",
            "BM.Standard2.52", "BM.Standard3.64",
            "VM.Standard.E3.Flex", "VM.Standard.E4.Flex"
        ]
        
        if config["compute_shape"] not in valid_compute_shapes:
            raise ValueError(f"Compute shape inválido para Oracle: {config['compute_shape']}")
    
    def _validate_database_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de Autonomous Database"""
        required_fields = ["workload_type", "compartment_id"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para Oracle Database: {field}")
        
        # Validar workload types soportados
        valid_workload_types = ["OLTP", "DW", "AJD", "APEX"]
        if config["workload_type"] not in valid_workload_types:
            raise ValueError(f"Workload type inválido para Oracle Database: {config['workload_type']}")
    
    def _validate_load_balancer_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica del Load Balancer de Oracle"""
        required_fields = ["compartment_id"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para Oracle Load Balancer: {field}")
        
        # Validar shapes válidos de Load Balancer
        valid_shapes = ["10Mbps", "100Mbps", "400Mbps", "8000Mbps"]
        shape = config.get("shape", "100Mbps")
        
        if shape not in valid_shapes:
            raise ValueError(f"Shape de load balancer inválido para Oracle: {shape}")
    
    def _validate_storage_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de Object Storage"""
        required_fields = ["namespace", "compartment_id"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para Oracle Storage: {field}")
        
        # Validar storage tiers válidos
        valid_storage_tiers = ["Standard", "InfrequentAccess", "Archive"]
        storage_tier = config.get("storage_tier", "Standard")
        
        if storage_tier not in valid_storage_tiers:
            raise ValueError(f"Storage tier inválido para Oracle: {storage_tier}")

    # ---------------------- Métodos de capacidades (expuestos al endpoint info) ----------------------
    def get_supported_compute_shapes(self) -> list[str]:
        return [
            "VM.Standard2.1", "VM.Standard2.2", "VM.Standard2.4", "VM.Standard2.8",
            "VM.Standard3.Flex", "VM.Optimized3.Flex", "BM.Standard2.52",
            "BM.Standard3.64", "VM.Standard.E3.Flex", "VM.Standard.E4.Flex"
        ]

    def get_supported_database_workloads(self) -> list[str]:
        return ["OLTP", "DW", "AJD", "APEX"]

    def get_supported_load_balancer_shapes(self) -> list[str]:
        return ["10Mbps", "100Mbps", "400Mbps", "8000Mbps"]

    def get_supported_storage_tiers(self) -> list[str]:
        return ["Standard", "InfrequentAccess", "Archive"]