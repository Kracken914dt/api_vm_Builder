from pydantic import BaseModel, Field


class AWSParams(BaseModel):
    instance_type: str = Field(..., example="t2.micro")
    region: str = Field(..., example="us-east-1")
    vpc: str
    ami: str
