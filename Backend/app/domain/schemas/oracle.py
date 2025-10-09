from pydantic import BaseModel, Field

class OracleParams(BaseModel):
    compute_shape: str = Field(..., example="VM.Standard2.1")
    compartment_id: str
    availability_domain: str
    subnet_id: str
    image_id: str