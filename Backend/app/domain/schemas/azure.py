from pydantic import BaseModel, Field


class AzureParams(BaseModel):
    size: str = Field(..., example="Standard_B1s")
    resource_group: str
    image: str
    vnet: str
