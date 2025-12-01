from fastapi import APIRouter, Query, Depends, status
from typing import Annotated, List

from src.stu_house_market.services.house_service import get_house_service, HouseService
from src.stu_house_market.core.oauth import get_user_from_login
from src.stu_house_market.model.user import Users
from src.stu_house_market.schema.house import PostHouse
from src.stu_house_market.model.house import PowerStability, WaterAccessibility
from src.stu_house_market.core.image_service import (
    generate_presigned_upload_urls,
    generate_presigned_download_urls,
)
from src.stu_house_market.schema.house import (
    PostHouse,
    ReturnHouse,
    UploadImageURLs,
    DownloadImageURLs,
)
from src.stu_house_market.core.exc import UnexpectedError

router = APIRouter(prefix="/house", tags=["House"])
house_service = Annotated[HouseService, Depends(get_house_service)]
current_user = Annotated[Users, Depends(get_user_from_login)]


@router.get("/upload_url", response_model=List[UploadImageURLs])
async def get_upload_url(image_count: int, user: current_user):
    return generate_presigned_upload_urls(image_count)


@router.get("/download_urls", response_model=List[DownloadImageURLs])
async def get_download_url(file_keys: List[str], user: current_user):
    return generate_presigned_download_urls(file_keys)


@router.get("/find", response_model=List[ReturnHouse])
async def search_house(
    user: current_user,
    institution: str = Query(None),
    location: str = Query(None),
    price: int = Query(None),
    max_price: int = Query(None),
    min_price: int = Query(None),
    bedroom_count: int = Query(None),
    min_bedroom_count: int = Query(None),
    max_bedroom_count: int = Query(None),
    water: WaterAccessibility = Query(None),
    power: PowerStability = Query(),
    wifi: bool = Query(None),
    parking_space: bool = Query(None),
    ac: bool = Query(None),
    kitchen: bool = Query(None),
    gym: bool = Query(None),
    tv: bool = Query(None),
):
    house_data = {
        "institution": institution,
        "location": location,
        "price": price,
        "max_price": max_price,
        "min_price": min_price,
        "bedroom_count": bedroom_count,
        "min_bedroom_count": min_bedroom_count,
        "max_bedroom_count": max_bedroom_count,
        "water": water,
        "power": power,
        "wifi": wifi,
        "parking_space": parking_space,
        "ac": ac,
        "kitchen": kitchen,
        "gym": gym,
        "tv": tv,
    }
    return await house_service.search_house(user.id, house_data)


@router.post("/list", status_code=status.HTTP_201_CREATED, response_model=ReturnHouse)
async def post_house(
    user: current_user, house: PostHouse, house_service: house_service
):
    new_house = await house_service.save_house(user.id, house.model_dump())
    if not new_house:
        raise UnexpectedError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to save given to the database --- Something Wrong with Data Field Given",
        )
    return new_house
