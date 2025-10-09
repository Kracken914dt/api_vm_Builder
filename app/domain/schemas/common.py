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

