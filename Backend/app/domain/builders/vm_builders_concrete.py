from __future__ import annotations
from typing import Dict, Any
from .vm_builder import VMBuilder


class AWSVMBuilder(VMBuilder):
    """Builder para AWS EC2 config."""

    def set_cpu_ram_by_tier(self, tier: str) -> "AWSVMBuilder":
        # Mapear tiers a instance types (simplificado)
        mapping = {
            "small": "t3.micro",
            "medium": "t3.small",
            "large": "t3.medium",
            "xlarge": "m5.large",
        }
        self._config["instance_type"] = mapping.get(tier, "t3.micro")
        return self

    def set_image_defaults(self) -> "AWSVMBuilder":
        self._config.setdefault("ami", "ami-0abcdef1234567890")
        return self

    def set_network_defaults(self) -> "AWSVMBuilder":
        self._config.setdefault("vpc_id", "vpc-12345678")
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)


class AzureVMBuilder(VMBuilder):
    """Builder para Azure VM config."""

    def set_cpu_ram_by_tier(self, tier: str) -> "AzureVMBuilder":
        mapping = {
            "small": "Standard_B1s",
            "medium": "Standard_B2s",
            "large": "Standard_D2s_v3",
            "xlarge": "Standard_D4s_v3",
        }
        self._config["vm_size"] = mapping.get(tier, "Standard_B1s")
        return self

    def set_image_defaults(self) -> "AzureVMBuilder":
        self._config.setdefault("image", "Ubuntu 20.04 LTS")
        return self

    def set_network_defaults(self) -> "AzureVMBuilder":
        self._config.setdefault("resource_group", "rg-default")
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)


class GCPVMBuilder(VMBuilder):
    """Builder para GCP Compute Engine config."""

    def set_cpu_ram_by_tier(self, tier: str) -> "GCPVMBuilder":
        mapping = {
            "small": "e2-micro",
            "medium": "e2-small",
            "large": "e2-medium",
            "xlarge": "e2-standard-2",
        }
        self._config["machine_type"] = mapping.get(tier, "e2-micro")
        return self

    def set_image_defaults(self) -> "GCPVMBuilder":
        # Imagen se maneja diferente en GCP; mantenemos simple
        self._config.setdefault("base_disk", "ubuntu-2004-lts")
        return self

    def set_network_defaults(self) -> "GCPVMBuilder":
        self._config.setdefault("zone", "us-central1-a")
        self._config.setdefault("project", "demo-project")
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)


class OnPremVMBuilder(VMBuilder):
    """Builder para OnPrem VM config."""

    def set_cpu_ram_by_tier(self, tier: str) -> "OnPremVMBuilder":
        mapping = {
            "small": (2, 4),
            "medium": (4, 8),
            "large": (8, 16),
            "xlarge": (16, 32),
        }
        cpu, ram = mapping.get(tier, (2, 4))
        self._config["cpu"] = cpu
        self._config["ram_gb"] = ram
        self._config.setdefault("disk_gb", 50)
        return self

    def set_image_defaults(self) -> "OnPremVMBuilder":
        # Para onPrem asumimos plantilla genérica
        return self

    def set_network_defaults(self) -> "OnPremVMBuilder":
        self._config.setdefault("nic", "eth0")
        self._config.setdefault("hypervisor", "vmware")
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)


class OracleVMBuilder(VMBuilder):
    """Builder para Oracle Compute config."""

    def set_cpu_ram_by_tier(self, tier: str) -> "OracleVMBuilder":
        mapping = {
            "small": "VM.Standard2.1",
            "medium": "VM.Standard2.2",
            "large": "VM.Standard2.4",
            "xlarge": "VM.Standard2.8",
        }
        self._config["compute_shape"] = mapping.get(tier, "VM.Standard2.1")
        return self

    def set_image_defaults(self) -> "OracleVMBuilder":
        self._config.setdefault("image_id", "ocid1.image.oc1..exampleimage")
        return self

    def set_network_defaults(self) -> "OracleVMBuilder":
        self._config.setdefault("compartment_id", "ocid1.compartment.oc1..exampleuniqueID")
        self._config.setdefault("availability_domain", "AD-1")
        self._config.setdefault("subnet_id", "ocid1.subnet.oc1..examplesubnet")
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)
