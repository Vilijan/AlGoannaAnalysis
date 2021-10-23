from pydantic import BaseModel
from typing import Optional


class NFT(BaseModel):
    creator: str
    nft_id: int
    name: str
    ipfs_image: Optional[str]
