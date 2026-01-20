from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Dict, Literal
from uuid import UUID

from src.stu_house_market.model.house import PowerStability, WaterAccessibility, EnvironmentSecurity
from src.stu_house_market.schema.user import User
from stu_house_market.utils.institutions_validator import _validate_institution


class PostHouse(BaseModel):
    institution: str
    location: str
    price: int
    bedroom: int
    description: str
    water: Optional[WaterAccessibility] = WaterAccessibility.no_nearby_water_source
    power: Optional[PowerStability] = PowerStability.not_stable
    security: Optional[EnvironmentSecurity] = EnvironmentSecurity.not_secured
    wifi: Optional[bool] = False
    parking_space: Optional[bool] = False
    ac: Optional[bool] = False
    kitchen: Optional[bool] = False
    gym: Optional[bool] = False
    tv: Optional[bool] = False
    images: List[Dict[Literal["file_key"], str]]

    @field_validator("institution")
    def validate_institution(cls, value: str):
        return _validate_institution(value)




class ReturnHouse(BaseModel):
    id: UUID
    owner_id : UUID
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

    model_config = ConfigDict(from_attributes=True)

class UploadImageURLs(BaseModel):
    file_key: str
    upload_url: str

class DownloadImageURLs(BaseModel):
    file_key: str
    download_url: str