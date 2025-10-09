"""
Abstract Factory para crear familias de productos de cloud.
Esta es la interfaz principal del patrón Abstract Factory.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .products import VirtualMachine, Database, LoadBalancer, Storage


class CloudAbstractFactory(ABC):
    """
    Abstract Factory que define la interfaz para crear familias de productos
    de cloud relacionados (VMs, Databases, Load Balancers, Storage).
    
    Cada proveedor de cloud (AWS, Azure, GCP, etc.) implementará esta interfaz
    para crear productos específicos de su plataforma.
    """
    
    @abstractmethod
    def create_virtual_machine(
        self, 
        name: str, 
        vm_config: Dict[str, Any]
    ) -> VirtualMachine:
        """Crea una máquina virtual específica del proveedor"""
        pass
    
    @abstractmethod
    def create_database(
        self, 
        name: str, 
        db_config: Dict[str, Any]
    ) -> Database:
        """Crea una base de datos específica del proveedor"""
        pass
    
    @abstractmethod
    def create_load_balancer(
        self, 
        name: str, 
        lb_config: Dict[str, Any]
    ) -> LoadBalancer:
        """Crea un load balancer específico del proveedor"""
        pass
    
    @abstractmethod
    def create_storage(
        self, 
        name: str, 
        storage_config: Dict[str, Any]
    ) -> Storage:
        """Crea un servicio de almacenamiento específico del proveedor"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        pass
    
    @abstractmethod
    def validate_region(self, region: str) -> bool:
        """Valida si la región es soportada por el proveedor"""
        pass


class CloudResourceManager:
    """
    Clase que utiliza el Abstract Factory para gestionar recursos de cloud.
    Esta clase sigue el principio de composición en lugar de herencia.
    """
    
    def __init__(self, factory: CloudAbstractFactory):
        self._factory = factory
        self._resources: Dict[str, Any] = {}
    
    def create_infrastructure(
        self, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea una infraestructura completa usando la factory.
        Este método demuestra cómo el Abstract Factory permite crear
        familias de productos relacionados.
        """
        infrastructure = {}
        
        # Crear VM si está especificada
        if 'vm' in config:
            vm = self._factory.create_virtual_machine(
                name=config['vm']['name'],
                vm_config=config['vm']['config']
            )
            infrastructure['vm'] = vm
            self._resources[vm.resource_id] = vm
        
        # Crear Database si está especificada
        if 'database' in config:
            db = self._factory.create_database(
                name=config['database']['name'],
                db_config=config['database']['config']
            )
            infrastructure['database'] = db
            self._resources[db.resource_id] = db
        
        # Crear Load Balancer si está especificado
        if 'load_balancer' in config:
            lb = self._factory.create_load_balancer(
                name=config['load_balancer']['name'],
                lb_config=config['load_balancer']['config']
            )
            infrastructure['load_balancer'] = lb
            self._resources[lb.resource_id] = lb
        
        # Crear Storage si está especificado
        if 'storage' in config:
            storage = self._factory.create_storage(
                name=config['storage']['name'],
                storage_config=config['storage']['config']
            )
            infrastructure['storage'] = storage
            self._resources[storage.resource_id] = storage
        
        return infrastructure
    
    def get_resource(self, resource_id: str) -> Optional[Any]:
        """Obtiene un recurso por su ID"""
        return self._resources.get(resource_id)
    
    def list_resources(self) -> Dict[str, Any]:
        """Lista todos los recursos gestionados"""
        return self._resources.copy()
    
    def get_provider_info(self) -> Dict[str, str]:
        """Obtiene información del proveedor actual"""
        return {
            'provider': self._factory.get_provider_name(),
            'total_resources': len(self._resources)
        }