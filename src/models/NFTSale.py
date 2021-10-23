from pydantic import BaseModel


class NFTSale(BaseModel):
    seller: str
    buyer: str
    price: float
    time: int
    asa_id: int
    sale_platform: str
