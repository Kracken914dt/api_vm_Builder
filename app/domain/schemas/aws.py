from pydantic import BaseModel, Field


class AWSParams(BaseModel):
    instance_type: str = Field(..., example="t2.micro")
    region: str = Field(..., example="us-east-1")
    vpc_id: str = Field(..., example="vpc-12345678")
    ami: str = Field(..., example="ami-0abcdef1234567890")
