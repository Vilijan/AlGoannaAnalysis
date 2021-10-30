from pydantic import BaseModel
from datetime import datetime


class ASAOwner(BaseModel):
    owner_address: str
    asa_id: int
    received_time: int

    @property
    def starting_day(self):
        return datetime.utcfromtimestamp(self.received_time).strftime('%Y-%m-%d')
