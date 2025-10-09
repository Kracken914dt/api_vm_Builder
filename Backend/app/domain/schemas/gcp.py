from pydantic import BaseModel, Field


class GCPParams(BaseModel):
    machine_type: str = Field(..., example="e2-micro")
    zone: str = Field(..., example="us-central1-a")
    base_disk: str
    project: str
