from pydantic import BaseModel
from typing import Optional, Literal


class House(BaseModel):
    uni: Optional[str] = None
    loc: Optional[str] = None
    max_price: Optional[int] = None
    min_price: Optional[int] = None
    bedroom: Optional[int] = None
    water: Optional[Literal[""]] = None
    power: Optional[Literal[""]] = None
    wifi: Optional[bool] = None
    park: Optional[bool] = None
    ac: Optional[bool] = None
    kitchen: Optional[bool] = None
    gym: Optional[bool] = None
    TV: Optional[bool] = None
