from typing import Optional, Union, Literal
from pydantic import BaseModel, Field
from .common import ProviderEnum
from .aws import AWSParams
from .azure import AzureParams
from .gcp import GCPParams
from .onpremise import OnPremParams
from .oracle import OracleParams

class VMCreateBase(BaseModel):
    name: str
    requested_by: Optional[str] = Field(default="system")


class VMCreateAWS(VMCreateBase):
    provider: Literal[ProviderEnum.aws]
    params: AWSParams


class VMCreateAzure(VMCreateBase):
    provider: Literal[ProviderEnum.azure]
    params: AzureParams


class VMCreateGCP(VMCreateBase):
    provider: Literal[ProviderEnum.gcp]
    params: GCPParams

class VMCreateOnPrem(VMCreateBase):
    provider: Literal[ProviderEnum.onpremise]
    params: OnPremParams

class VMCreateOracle(VMCreateBase):
    provider: Literal[ProviderEnum.oracle]
    params: OracleParams

VMCreateRequest = Union[VMCreateAWS, VMCreateAzure, VMCreateGCP, VMCreateOnPrem, VMCreateOracle]
