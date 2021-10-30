from pydantic import BaseModel
from typing import Optional


class ASA(BaseModel):
    creator: str
    asa_id: int
    name: str
    supply: int
    ipfs_image: Optional[str]
