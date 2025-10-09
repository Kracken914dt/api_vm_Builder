"""
Factory Provider que implementa completamente el patrón Abstract Factory
reemplazando el patrón Factory Method anterior.

Este módulo implementa todos los principios SOLID:
- SRP: Solo se encarga de proveer las factories correctas
- OCP: Fácil añadir nuevos proveedores sin modificar código existente
- LSP: Todas las factories implementan la misma interfaz
- ISP: Interfaces segregadas por tipo de recurso
- DIP: Depende de abstracciones, no de implementaciones concretas
"""
from typing import Dict, Type
from enum import Enum
from .abstractions.factory import CloudAbstractFactory
from .factories_concrete.aws_factory import AWSCloudFactory
from .factories_concrete.azure_factory import AzureCloudFactory
from .factories_concrete.gcp_factory import GCPCloudFactory
from .factories_concrete.oracle_factory import OracleCloudFactory
from .factories_concrete.onprem_factory import OnPremiseCloudFactory


class CloudProvider(str, Enum):
    """Enumeración de proveedores de cloud soportados"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE = "oracle"
    ONPREM = "onprem"


class FactoryProvider:
    """
    Provider que implementa el patrón Factory Method para obtener 
    las Abstract Factories correspondientes a cada proveedor.
    """
    
    def __init__(self):
        # Registro de factories disponibles (patrón Registry)
        self._factories: Dict[CloudProvider, Type[CloudAbstractFactory]] = {}
        self._register_default_factories()
    
    def _register_default_factories(self) -> None:
        """Registra todas las factories implementadas - Abstract Factory completo"""
        self.register_factory(CloudProvider.AWS, AWSCloudFactory)
        self.register_factory(CloudProvider.AZURE, AzureCloudFactory)
        self.register_factory(CloudProvider.GCP, GCPCloudFactory)
        self.register_factory(CloudProvider.ORACLE, OracleCloudFactory)
        self.register_factory(CloudProvider.ONPREM, OnPremiseCloudFactory)
    
    def register_factory(
        self, 
        provider: CloudProvider, 
        factory_class: Type[CloudAbstractFactory]
    ) -> None:
        """Registra una nueva factory para un proveedor (OCP - Open/Closed Principle)"""
        self._factories[provider] = factory_class
        print(f"✅ Abstract Factory registrada para proveedor: {provider.value}")
    
    def get_factory(self, provider: CloudProvider) -> CloudAbstractFactory:
        """
        Factory Method principal: retorna la Abstract Factory apropiada.
        REEMPLAZA completamente el patrón Factory Method anterior.
        """
        if provider not in self._factories:
            available_providers = list(self._factories.keys())
            raise ValueError(
                f"Proveedor '{provider}' no soportado. "
                f"Proveedores disponibles: {[p.value for p in available_providers]}"
            )
        
        factory_class = self._factories[provider]
        factory_instance = factory_class()
        
        print(f"🏭 Abstract Factory Provider: Creando factory para {provider.value}")
        return factory_instance
    
    def get_available_providers(self) -> list[str]:
        """Retorna la lista de proveedores disponibles"""
        return [provider.value for provider in self._factories.keys()]
    
    def is_provider_supported(self, provider: CloudProvider) -> bool:
        """Verifica si un proveedor está soportado"""
        return provider in self._factories
    
    def get_provider_capabilities(self, provider: CloudProvider) -> Dict[str, any]:
        """Obtiene las capacidades de un proveedor específico"""
        if not self.is_provider_supported(provider):
            raise ValueError(f"Proveedor {provider} no soportado")
            
        factory = self.get_factory(provider)
        return factory.get_provider_info()


# Instancia global del provider (Singleton pattern)
_factory_provider = FactoryProvider()


def create_cloud_factory(provider: CloudProvider) -> CloudAbstractFactory:
    """
    Función principal para crear Abstract Factories.
    REEMPLAZA la función get_factory del patrón Factory Method anterior.
    """
    return _factory_provider.get_factory(provider)


def get_available_providers() -> list[str]:
    """Función de conveniencia para obtener proveedores disponibles"""
    return _factory_provider.get_available_providers()


def get_provider_capabilities(provider: CloudProvider) -> Dict[str, any]:
    """Obtiene información detallada sobre las capacidades de un proveedor"""
    return _factory_provider.get_provider_capabilities(provider)


def register_custom_factory(
    provider: CloudProvider, 
    factory_class: Type[CloudAbstractFactory]
) -> None:
    """Función para registrar factories personalizadas (extensibilidad)"""
    _factory_provider.register_factory(provider, factory_class)


def is_provider_supported(provider_str: str) -> bool:
    """Verifica si un proveedor (como string) está soportado"""
    try:
        provider = CloudProvider(provider_str)
        return _factory_provider.is_provider_supported(provider)
    except ValueError:
        return False