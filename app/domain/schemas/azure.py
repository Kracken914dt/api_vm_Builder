from pydantic import BaseModel, Field


class AzureParams(BaseModel):
    vm_size: str = Field(..., example="Standard_B1s")
    resource_group: str = Field(..., example="rg-default")
    image: str = Field(..., example="Ubuntu 20.04 LTS")
    region: str = Field(..., example="eastus")
