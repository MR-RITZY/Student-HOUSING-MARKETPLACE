from fastapi import APIRouter, Query


router = APIRouter()


@router.get("/")
async def find_house(
    uni: str = Query(None),
    loc: str = Query(None),
    max_price: int = Query(None),
    min_price: int = Query(None),
    bedroom: int = Query(None),
    water: str = Query(None, regex=""),
    power: str = Query(None, regex=""),
    wifi: bool = Query(None),
    park: bool = Query(None),
    ac: bool = Query(None),
    kitchen: bool = Query(None),
    gym: bool = Query(None),
    tv: bool = Query(None)
):
    pass


@router.post("/")
async def list_house():
    pass
