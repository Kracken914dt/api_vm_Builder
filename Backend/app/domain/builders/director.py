from __future__ import annotations
from typing import Dict, Any
from .vm_builder import Director, VMBuilder


class VMTierDirector(Director):
    """
    Director que aplica la lógica de negocio de CPU/RAM por tipo de VM (tier)
    y construye la configuración base por proveedor usando un Builder.
    """

    def construct(self, builder: VMBuilder, *, name: str, region: str, tier: str) -> Dict[str, Any]:
        builder.reset()
        builder.set_name(name)
        builder.set_region(region)
        builder.set_cpu_ram_by_tier(tier)
        builder.set_image_defaults()
        builder.set_network_defaults()
        return builder.build()
