from __future__ import annotations
from typing import Dict, Any, Optional, List
from .vm_builder import Director, VMBuilder
from app.domain.schemas.common import VMProfile


class VMTierDirector(Director):
    """
    Director que aplica la lógica de negocio de CPU/RAM por tipo de VM (tier)
    y construye la configuración base por proveedor usando un Builder.
    """

    def construct(
        self,
        builder: VMBuilder,
        *,
        name: str,
        region: str,
        tier: str,
        profile: VMProfile = VMProfile.general,
        key_pair_name: Optional[str] = None,
        firewall_rules: Optional[List[str]] = None,
        public_ip: Optional[bool] = None,
        memory_optimization: Optional[bool] = None,
        disk_optimization: Optional[bool] = None,
        storage_iops: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Construye la configuración base y añade metadatos comunes (vcpus/memory_gb) y opcionales del PDF.
        - profile ajusta la familia (general|memory|compute) además del tier.
        - Los opcionales se agregan al config para que la Abstract Factory los consuma si aplica.
        """
        builder.reset()
        builder.set_name(name)
        builder.set_region(region)

        # 1) Selección de CPU/RAM según perfil + tier (valores didácticos por proveedor)
        # La traducción específica a instance_type/vm_size/machine_type la hace el builder
        builder.set_cpu_ram_by_tier(self._resolve_effective_tier(profile, tier))

        # 2) Defaults de imagen y red por proveedor
        builder.set_image_defaults()
        builder.set_network_defaults()

        # 3) Adjuntar opcionales estándar si se proporcionan (quedan en el dict final)
        config = builder.peek()
        # Asegurar estructura común
        if key_pair_name is not None:
            config["key_pair"] = key_pair_name
        if firewall_rules is not None:
            config["firewall_rules"] = firewall_rules
        if public_ip is not None:
            config["public_ip"] = public_ip
        if memory_optimization is not None:
            config["memory_optimization"] = memory_optimization
        if disk_optimization is not None:
            config["disk_optimization"] = disk_optimization
        if storage_iops is not None:
            config["storage_iops"] = storage_iops

        # 4) Añadir anotaciones didácticas de vCPU/RAM (derivadas de tier genérico)
        vcpus, mem_gb = self._tier_to_compute(tier)
        config.setdefault("vcpus", vcpus)
        config.setdefault("memory_gb", mem_gb)

        return builder.build()

    def _resolve_effective_tier(self, profile: VMProfile, tier: str) -> str:
        """Permite ajustar el tier si el perfil requiere otra familia de tipos.
        Por ahora devolvemos el mismo tier; el mapping por proveedor se hace en cada builder
        con su propia tabla por perfil si fuera necesario. Esta función queda para futura expansión.
        """
        return tier

    def _tier_to_compute(self, tier: str) -> tuple[int, int]:
        """Conversión didáctica de tier a (vCPUs, RAM GiB), usada para exponer en specs."""
        mapping = {
            "small": (2, 4),
            "medium": (4, 8),
            "large": (8, 16),
            "xlarge": (16, 32),
        }
        return mapping.get(tier, (2, 4))
