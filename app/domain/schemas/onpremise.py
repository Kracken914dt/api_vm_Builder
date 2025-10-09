from pydantic import BaseModel


class OnPremParams(BaseModel):
    cpu: int
    ram_gb: int
    disk_gb: int
    nic: str
