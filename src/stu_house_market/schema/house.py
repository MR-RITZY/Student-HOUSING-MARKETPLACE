from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Literal
from uuid import UUID

from src.stu_house_market.model.house import PowerStability, WaterAccessibility
from src.stu_house_market.schema.user import User


class PostHouse(BaseModel):
    institution: str
    location: str
    price: int
    bedroom: int
    water: Optional[WaterAccessibility] = WaterAccessibility.no_nearby_water_source
    power: Optional[PowerStability] = PowerStability.not_stable
    wifi: Optional[bool] = None
    parking_space: Optional[bool] = None
    ac: Optional[bool] = None
    kitchen: Optional[bool] = None
    gym: Optional[bool] = None
    tv: Optional[bool] = None
    images: List[Dict[Literal["file_key"], str]]


class ReturnHouse(BaseModel):
    id: UUID
    user_id : UUID
    institution: str
    location: str
    price: int
    bedroom: int
    water: WaterAccessibility
    power: PowerStability
    wifi: bool
    parking_space: bool
    ac: bool
    kitchen: bool
    gym: bool
    tv: bool
    images: List[Dict[str, str]]
    user: User

    model_config = ConfigDict(from_attributes=True)

class UploadImageURLs(BaseModel):
    file_key: str
    upload_url: str

class DownloadImageURLs(BaseModel):
    file_key: str
    download_url: str