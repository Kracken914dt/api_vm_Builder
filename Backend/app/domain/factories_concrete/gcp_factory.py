
from typing import Dict, Any
from ..abstractions.factory import CloudAbstractFactory
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage
from ..products.gcp_products import ComputeEngineInstance, CloudSQLDatabase, CloudLoadBalancer, CloudStorage


class GCPCloudFactory(CloudAbstractFactory):
    """
    Fábrica concreta para crear productos de Google Cloud Platform.
    Implementa el Abstract Factory pattern para GCP.
    """
    
    def __init__(self):
        self.provider_name = "gcp"
        self.supported_regions = [
            "us-central1", "us-east1", "us-west1", "us-west2",
            "europe-west1", "europe-west2", "asia-east1", "asia-southeast1"
        ]
    
    def create_virtual_machine(self, name: str, config: Dict[str, Any]) -> VirtualMachine:
        """
        Crea una instancia de Compute Engine con la configuración especificada.
        
        Args:
            config: Configuración de la VM incluyendo machine_type, zone, etc.
            
        Returns:
            ComputeEngineInstance: Nueva instancia de VM de GCP
        """
        # Validar configuración específica de GCP
        self._validate_vm_config(config)
        config = config.copy()
        config["name"] = name
        
        # Crear la instancia de Compute Engine
        vm = ComputeEngineInstance(config)
        print(f"🏭 GCP Factory: Creando Compute Engine instance {vm.name}")
        
        return vm
    
    def create_database(self, name: str, config: Dict[str, Any]) -> Database:
        """
        Crea una instancia de Cloud SQL con la configuración especificada.
        
        Args:
            config: Configuración de la base de datos incluyendo engine, tier, etc.
            
        Returns:
            CloudSQLDatabase: Nueva instancia de base de datos de GCP
        """
        # Validar configuración específica de GCP
        self._validate_database_config(config)
        config = config.copy()
        config["name"] = name
        
        # Crear la instancia de Cloud SQL
        database = CloudSQLDatabase(config)
        print(f"🏭 GCP Factory: Creando Cloud SQL database {database.name}")
        
        return database
    
    def create_load_balancer(self, name: str, config: Dict[str, Any]) -> LoadBalancer:
        """
        Crea un Load Balancer de GCP con la configuración especificada.
        
        Args:
            config: Configuración del load balancer incluyendo type, region, etc.
            
        Returns:
            CloudLoadBalancer: Nueva instancia de load balancer de GCP
        """
        # Validar configuración específica de GCP
        self._validate_load_balancer_config(config)
        config = config.copy()
        config["name"] = name
        
        # Crear el Load Balancer
        load_balancer = CloudLoadBalancer(config)
        print(f"🏭 GCP Factory: Creando Cloud Load Balancer {load_balancer.name}")
        
        return load_balancer
    
    def create_storage(self, name: str, config: Dict[str, Any]) -> Storage:
        """
        Crea un bucket de Cloud Storage con la configuración especificada.
        
        Args:
            config: Configuración del storage incluyendo location, storage_class, etc.
            
        Returns:
            CloudStorage: Nueva instancia de storage de GCP
        """
        # Validar configuración específica de GCP
        self._validate_storage_config(config)
        config = config.copy()
        config["name"] = name
        
        # Crear el Cloud Storage bucket
        storage = CloudStorage(config)
        print(f"🏭 GCP Factory: Creando Cloud Storage bucket {storage.name}")
        
        return storage
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna información sobre el proveedor GCP"""
        return {
            "name": "Google Cloud Platform",
            "code": "gcp",
            "supported_regions": self.supported_regions,
            "services": {
                "compute": "Compute Engine",
                "database": "Cloud SQL",
                "load_balancer": "Cloud Load Balancing",
                "storage": "Cloud Storage"
            }
        }
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "Google Cloud Platform"
    
    def validate_region(self, region: str) -> bool:
        """Valida si la región es soportada por GCP"""
        return region in self.supported_regions
    
    def _validate_vm_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de Compute Engine"""
        required_fields = ["machine_type"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para GCP VM: {field}")
        
        # Validar machine types válidos de GCP
        valid_machine_types = [
            "e2-micro", "e2-small", "e2-medium", "e2-standard-2", "e2-standard-4",
            "n1-standard-1", "n1-standard-2", "n1-standard-4", "n1-standard-8",
            "n2-standard-2", "n2-standard-4", "n2-standard-8"
        ]
        
        if config["machine_type"] not in valid_machine_types:
            raise ValueError(f"Machine type inválido para GCP: {config['machine_type']}")
    
    def _validate_database_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de Cloud SQL"""
        required_fields = ["engine"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Campo requerido faltante para GCP Database: {field}")
        
        # Validar engines soportados
        valid_engines = ["mysql", "postgres", "sqlserver"]
        if config["engine"] not in valid_engines:
            raise ValueError(f"Engine de base de datos inválido para GCP: {config['engine']}")
    
    def _validate_load_balancer_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica del Load Balancer de GCP"""
        # Validar tipos de load balancer válidos
        valid_types = ["HTTP(S)", "TCP", "UDP", "SSL"]
        lb_type = config.get("type", "HTTP(S)")
        
        if lb_type not in valid_types:
            raise ValueError(f"Tipo de load balancer inválido para GCP: {lb_type}")
    
    def _validate_storage_config(self, config: Dict[str, Any]) -> None:
        """Valida la configuración específica de Cloud Storage"""
        # Validar storage classes válidos
        valid_storage_classes = ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"]
        storage_class = config.get("storage_class", "STANDARD")
        
        if storage_class not in valid_storage_classes:
            raise ValueError(f"Storage class inválido para GCP: {storage_class}")
        
        # Validar ubicaciones válidas
        valid_locations = ["US", "EU", "ASIA"] + self.supported_regions
        location = config.get("location", "US")
        
        if location not in valid_locations:
            raise ValueError(f"Ubicación inválida para GCP Storage: {location}")

    # ---------------------- Métodos de capacidades (expuestos al endpoint info) ----------------------
    def get_supported_machine_types(self) -> list[str]:
        return [
            "e2-micro", "e2-small", "e2-medium", "e2-standard-2", "e2-standard-4",
            "n1-standard-1", "n1-standard-2", "n1-standard-4", "n1-standard-8",
            "n2-standard-2", "n2-standard-4", "n2-standard-8"
        ]

    def get_supported_database_engines(self) -> list[str]:
        return ["mysql", "postgres", "sqlserver"]

    def get_supported_storage_classes(self) -> list[str]:
        return ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"]

    def get_supported_load_balancer_types(self) -> list[str]:
        return ["HTTP(S)", "TCP", "UDP", "SSL"]

    def get_supported_locations(self) -> list[str]:
        return ["US", "EU", "ASIA"] + self.supported_regions