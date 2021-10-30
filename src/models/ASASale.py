from pydantic import BaseModel


class ASASale(BaseModel):
    seller: str
    buyer: str
    price: float
    time: int
    asa_id: int
    sale_platform: str
