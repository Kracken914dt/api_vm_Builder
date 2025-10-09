from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any


class VMBuilder(ABC):
    """
    Builder abstracto para construir configuraciones de VM por proveedor.
    La salida es un dict config listo para pasarlo a la Abstract Factory
    correspondiente (create_virtual_machine(name, config)).
    """

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._name: str = ""

    def reset(self) -> None:
        self._config = {}
        self._name = ""

    def set_name(self, name: str) -> "VMBuilder":
        self._name = name
        return self

    def set_region(self, region: str) -> "VMBuilder":
        self._config["region"] = region
        return self

    def peek(self) -> Dict[str, Any]:
        """Devuelve una referencia al config interno para permitir ajustes del Director.
        Nota: se usa intencionalmente para inyectar opcionales comunes antes de build().
        """
        return self._config

    @abstractmethod
    def set_cpu_ram_by_tier(self, tier: str) -> "VMBuilder":
        """Asigna valores de CPU/RAM en función del tier (small/medium/large/etc)."""
        raise NotImplementedError

    @abstractmethod
    def set_image_defaults(self) -> "VMBuilder":
        """Establece imagen por defecto para el proveedor."""
        raise NotImplementedError

    @abstractmethod
    def set_network_defaults(self) -> "VMBuilder":
        """Establece red/VPC/VNet por defecto para el proveedor."""
        raise NotImplementedError

    @abstractmethod
    def build(self) -> Dict[str, Any]:
        """Retorna el dict de configuración final de la VM para el proveedor."""
        raise NotImplementedError


class Director(ABC):
    """Interfaz de un Director."""

    @abstractmethod
    def construct(self, builder: VMBuilder, *, name: str, region: str, tier: str, **kwargs: Any) -> Dict[str, Any]:
        raise NotImplementedError
