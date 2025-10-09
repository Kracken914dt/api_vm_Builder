"""
Productos concretos de AWS para el patrón Abstract Factory.
Estos implementan las interfaces abstractas para los servicios específicos de AWS.
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class EC2Instance(VirtualMachine):
    """Implementación concreta de VM para AWS (EC2)"""
    
    def __init__(self, name: str, region: str, instance_type: str, ami: str, vpc_id: str):
        super().__init__(f"i-{uuid.uuid4().hex[:8]}", name, region)
        self.instance_type = instance_type
        self.ami = ami
        self.vpc_id = vpc_id
        self.security_groups: List[str] = []
        self.key_pair: str = ""
        self.private_ip: str = ""
        self.public_ip: str = ""
    
    def get_resource_type(self) -> str:
        return "AWS::EC2::Instance"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "instance_type": self.instance_type,
            "ami": self.ami,
            "vpc_id": self.vpc_id,
            "region": self.region,
            "security_groups": self.security_groups,
            "private_ip": self.private_ip,
            "public_ip": self.public_ip
        }
    
    def start(self) -> None:
        """Inicia la instancia EC2"""
        if self.status == ResourceStatus.STOPPED:
            self.status = ResourceStatus.RUNNING
            print(f"✅ EC2 Instance {self.name} started in region {self.region}")
        else:
            raise ValueError(f"Cannot start instance in state {self.status}")
    
    def stop(self) -> None:
        """Detiene la instancia EC2"""
        if self.status == ResourceStatus.RUNNING:
            self.status = ResourceStatus.STOPPED
            print(f"⏹️ EC2 Instance {self.name} stopped")
        else:
            raise ValueError(f"Cannot stop instance in state {self.status}")
    
    def restart(self) -> None:
        """Reinicia la instancia EC2"""
        if self.status == ResourceStatus.RUNNING:
            print(f"🔄 EC2 Instance {self.name} restarting...")
            # Simula reinicio
            self.status = ResourceStatus.RUNNING
        else:
            raise ValueError(f"Cannot restart instance in state {self.status}")
    
    def resize(self, new_instance_type: str) -> None:
        """Cambia el tipo de instancia"""
        old_type = self.instance_type
        self.instance_type = new_instance_type
        print(f"📏 EC2 Instance {self.name} resized from {old_type} to {new_instance_type}")


class RDSDatabase(Database):
    """Implementación concreta de Database para AWS (RDS)"""
    
    def __init__(self, name: str, region: str, engine: str, instance_class: str, allocated_storage: int):
        super().__init__(f"db-{uuid.uuid4().hex[:8]}", name, region)
        self.engine = engine
        self.instance_class = instance_class
        self.allocated_storage = allocated_storage
        self.endpoint: str = f"{name}.{region}.rds.amazonaws.com"
        self.port: int = 3306 if engine == "mysql" else 5432
    
    def get_resource_type(self) -> str:
        return "AWS::RDS::DBInstance"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "engine": self.engine,
            "instance_class": self.instance_class,
            "allocated_storage": self.allocated_storage,
            "endpoint": self.endpoint,
            "port": self.port,
            "region": self.region
        }
    
    def backup(self) -> str:
        """Crea un snapshot de RDS"""
        backup_id = f"snap-{uuid.uuid4().hex[:8]}"
        print(f"📋 RDS Database {self.name} backup created: {backup_id}")
        return backup_id
    
    def restore(self, backup_id: str) -> None:
        """Restaura desde un snapshot"""
        print(f"🔄 RDS Database {self.name} restored from backup: {backup_id}")
    
    def scale(self, new_instance_class: str) -> None:
        """Escala la instancia RDS"""
        old_class = self.instance_class
        self.instance_class = new_instance_class
        print(f"📈 RDS Database {self.name} scaled from {old_class} to {new_instance_class}")


class ApplicationLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para AWS (ALB)"""
    
    def __init__(self, name: str, region: str, vpc_id: str, scheme: str = "internet-facing"):
        super().__init__(f"alb-{uuid.uuid4().hex[:8]}", name, region)
        self.vpc_id = vpc_id
        self.scheme = scheme
        self.targets: List[str] = []
        self.listeners: List[Dict[str, Any]] = []
        self.dns_name = f"{name}-{self.resource_id[-8:]}.{region}.elb.amazonaws.com"
    
    def get_resource_type(self) -> str:
        return "AWS::ElasticLoadBalancingV2::LoadBalancer"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "vpc_id": self.vpc_id,
            "scheme": self.scheme,
            "dns_name": self.dns_name,
            "targets": self.targets,
            "listeners": self.listeners,
            "region": self.region
        }
    
    def add_target(self, target_id: str) -> None:
        """Añade un target al ALB"""
        if target_id not in self.targets:
            self.targets.append(target_id)
            print(f"🎯 Target {target_id} added to ALB {self.name}")
    
    def remove_target(self, target_id: str) -> None:
        """Remueve un target del ALB"""
        if target_id in self.targets:
            self.targets.remove(target_id)
            print(f"❌ Target {target_id} removed from ALB {self.name}")
    
    def configure_health_check(self, config: Dict[str, Any]) -> None:
        """Configura health checks"""
        health_check = {
            "path": config.get("path", "/health"),
            "interval": config.get("interval", 30),
            "timeout": config.get("timeout", 5),
            "healthy_threshold": config.get("healthy_threshold", 2)
        }
        print(f"❤️ Health check configured for ALB {self.name}: {health_check}")


class S3Storage(Storage):
    """Implementación concreta de Storage para AWS (S3)"""
    
    def __init__(self, name: str, region: str, storage_class: str = "STANDARD"):
        super().__init__(f"s3-{uuid.uuid4().hex[:8]}", name, region)
        self.bucket_name = name
        self.storage_class = storage_class
        self.objects: Dict[str, Dict[str, Any]] = {}
        self.versioning_enabled = False
    
    def get_resource_type(self) -> str:
        return "AWS::S3::Bucket"
    
    def get_specs(self) -> Dict[str, Any]:
        return {
            "bucket_name": self.bucket_name,
            "storage_class": self.storage_class,
            "region": self.region,
            "versioning_enabled": self.versioning_enabled,
            "object_count": len(self.objects)
        }
    
    def create_bucket(self, bucket_name: str) -> None:
        """Crea un bucket S3 (ya creado en el constructor)"""
        print(f"🪣 S3 Bucket {bucket_name} created in region {self.region}")
    
    def upload_file(self, file_path: str, key: str) -> None:
        """Simula la subida de un archivo a S3"""
        self.objects[key] = {
            "size": 1024,  # Simulado
            "last_modified": "2024-01-01T00:00:00Z",
            "storage_class": self.storage_class
        }
        print(f"⬆️ File uploaded to S3: s3://{self.bucket_name}/{key}")
    
    def download_file(self, key: str, local_path: str) -> None:
        """Simula la descarga de un archivo desde S3"""
        if key in self.objects:
            print(f"⬇️ File downloaded from S3: s3://{self.bucket_name}/{key} -> {local_path}")
        else:
            raise FileNotFoundError(f"Object {key} not found in bucket {self.bucket_name}")


class EC2NetworkInterface(NetworkInterface):
    """Implementación de interfaz de red para EC2"""
    
    def __init__(self, instance_id: str):
        self.instance_id = instance_id
        self.security_groups: List[str] = []
        self.public_ip: str = ""
    
    def configure_security_group(self, rules: Dict[str, Any]) -> None:
        """Configura security groups"""
        sg_id = f"sg-{uuid.uuid4().hex[:8]}"
        self.security_groups.append(sg_id)
        print(f"🔒 Security group {sg_id} configured for instance {self.instance_id}")
    
    def assign_public_ip(self) -> str:
        """Asigna una IP pública elástica"""
        self.public_ip = f"54.{uuid.uuid4().int % 256}.{uuid.uuid4().int % 256}.{uuid.uuid4().int % 256}"
        print(f"🌐 Public IP {self.public_ip} assigned to instance {self.instance_id}")
        return self.public_ip