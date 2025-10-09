"""
Fábrica concreta de AWS que implementa el Abstract Factory.
Crea familias de productos específicos de AWS que trabajan juntos.
"""
from typing import Dict, Any
from ..abstractions.factory import CloudAbstractFactory
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage
from ..products.aws_products import EC2Instance, RDSDatabase, ApplicationLoadBalancer, S3Storage


class AWSCloudFactory(CloudAbstractFactory):
    """
    Fábrica concreta para crear productos de AWS.
    Implementa el Abstract Factory pattern para AWS.
    """
    
    def __init__(self):
        self._supported_regions = {
            "us-east-1", "us-west-1", "us-west-2", "eu-west-1", 
            "eu-central-1", "ap-southeast-1", "ap-northeast-1"
        }
    
    def create_virtual_machine(self, name: str, vm_config: Dict[str, Any]) -> VirtualMachine:
        """Crea una instancia EC2"""
        required_fields = ["instance_type", "ami", "vpc_id", "region"]
        self._validate_config(vm_config, required_fields)
        
        region = vm_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by AWS")
        
        vm = EC2Instance(
            name=name,
            region=region,
            instance_type=vm_config["instance_type"],
            ami=vm_config["ami"],
            vpc_id=vm_config["vpc_id"]
        )
        
        # Configuraciones opcionales
        if "security_groups" in vm_config:
            vm.security_groups = vm_config["security_groups"]
        if "key_pair" in vm_config:
            vm.key_pair = vm_config["key_pair"]
        
        print(f"🏭 AWS Factory: Created EC2 Instance {name} ({vm_config['instance_type']})")
        return vm
    
    def create_database(self, name: str, db_config: Dict[str, Any]) -> Database:
        """Crea una instancia RDS"""
        required_fields = ["engine", "instance_class", "allocated_storage", "region"]
        self._validate_config(db_config, required_fields)
        
        region = db_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by AWS")
        
        db = RDSDatabase(
            name=name,
            region=region,
            engine=db_config["engine"],
            instance_class=db_config["instance_class"],
            allocated_storage=db_config["allocated_storage"]
        )
        
        print(f"🏭 AWS Factory: Created RDS Database {name} ({db_config['engine']})")
        return db
    
    def create_load_balancer(self, name: str, lb_config: Dict[str, Any]) -> LoadBalancer:
        """Crea un Application Load Balancer"""
        required_fields = ["vpc_id", "region"]
        self._validate_config(lb_config, required_fields)
        
        region = lb_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by AWS")
        
        lb = ApplicationLoadBalancer(
            name=name,
            region=region,
            vpc_id=lb_config["vpc_id"],
            scheme=lb_config.get("scheme", "internet-facing")
        )
        
        # Configurar listeners por defecto
        if "listeners" in lb_config:
            lb.listeners = lb_config["listeners"]
        
        print(f"🏭 AWS Factory: Created Application Load Balancer {name}")
        return lb
    
    def create_storage(self, name: str, storage_config: Dict[str, Any]) -> Storage:
        """Crea un bucket S3"""
        required_fields = ["region"]
        self._validate_config(storage_config, required_fields)
        
        region = storage_config["region"]
        if not self.validate_region(region):
            raise ValueError(f"Region {region} not supported by AWS")
        
        storage = S3Storage(
            name=name,
            region=region,
            storage_class=storage_config.get("storage_class", "STANDARD")
        )
        
        # Configurar versionado si se especifica
        if storage_config.get("versioning_enabled"):
            storage.versioning_enabled = True
        
        print(f"🏭 AWS Factory: Created S3 Bucket {name}")
        return storage
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna información completa sobre el proveedor AWS"""
        return {
            "name": "Amazon Web Services",
            "code": "aws",
            "supported_regions": self._supported_regions,
            "services": {
                "compute": "EC2 Instances",
                "database": "RDS",
                "load_balancer": "Application Load Balancer",
                "storage": "S3"
            }
        }
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "Amazon Web Services (AWS)"
    
    def validate_region(self, region: str) -> bool:
        """Valida si la región es soportada por AWS"""
        return region in self._supported_regions
    
    def _validate_config(self, config: Dict[str, Any], required_fields: list) -> None:
        """Valida que la configuración tenga los campos requeridos"""
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(f"Missing required fields for AWS: {missing_fields}")
    
    def get_supported_regions(self) -> set:
        """Retorna las regiones soportadas"""
        return self._supported_regions.copy()
    
    def get_recommended_instance_types(self) -> Dict[str, list]:
        """Retorna tipos de instancia recomendados por caso de uso"""
        return {
            "general": ["t3.micro", "t3.small", "t3.medium", "m5.large"],
            "compute": ["c5.large", "c5.xlarge", "c5.2xlarge"],
            "memory": ["r5.large", "r5.xlarge", "r5.2xlarge"],
            "storage": ["i3.large", "i3.xlarge", "d2.xlarge"]
        }