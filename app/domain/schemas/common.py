from enum import Enum
from typing import Literal, Optional, List, Union
from pydantic import BaseModel, Field


class ProviderEnum(str, Enum):
    aws = "aws"
    azure = "azure"
    gcp = "gcp"
    onpremise = "onpremise"
    oracle = "oracle" 
    
class VMTier(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"
    xlarge = "xlarge"

class VMProfile(str, Enum):
    """Familias de máquina según el PDF: general, memory-optimized, compute-optimized."""
    general = "general"
    memory = "memory"
    compute = "compute"

class VMUpdateRequest(BaseModel):
    name: Optional[str] = None
    cpu: Optional[int] = None
    ram_gb: Optional[int] = None
    disk_gb: Optional[int] = None
    instance_type: Optional[str] = None
    size: Optional[str] = None
    machine_type: Optional[str] = None


class VMActionRequest(BaseModel):
    action: Literal["start", "stop", "restart"]
    requested_by: Optional[str] = Field(default="system")


class VMDTO(BaseModel):
    id: str
    name: str
    provider: ProviderEnum
    status: str
    specs: dict


class VMResponse(BaseModel):
    success: bool
    vm: Optional[VMDTO]
    error: Optional[str] = None


class VMListResponse(BaseModel):
    items: List[VMDTO]


class VMBuildRequest(BaseModel):
    name: str = Field(..., example="web-01")
    provider: ProviderEnum
    region: str = Field(..., example="us-east-1")
    tier: VMTier = Field(..., example="small", description="Nivel de VM: small|medium|large|xlarge")
    # Perfil/familia de la VM (opcional); por defecto general-purpose
    profile: VMProfile = Field(default=VMProfile.general, description="Familia de máquina: general|memory|compute")
    # Opcionales del PDF
    key_pair_name: Optional[str] = Field(default=None, description="Clave SSH o autenticación (keyPairName)")
    firewall_rules: Optional[List[str]] = Field(default=None, description="Reglas de seguridad (firewallRules)")
    public_ip: Optional[bool] = Field(default=None, description="Asignar IP pública (publicIP)")
    memory_optimization: Optional[bool] = Field(default=None, description="Optimización de memoria (memoryOptimization)")
    disk_optimization: Optional[bool] = Field(default=None, description="Optimización de disco (diskOptimization)")
    # Campo opcional de ejemplo de storage (iops) del PDF
    storage_iops: Optional[int] = Field(default=None, description="Rendimiento del disco (iops)")

