from uuid import uuid4
from itsdangerous import URLSafeTimedSerializer


from src.stu_house_market.core.config import settings


serializer = URLSafeTimedSerializer(
    settings.SAFE_URL_SECRET, salt="Student Housing Marketplace Safe URL"
)


def get_safe_token(token_data: dict):
    updated_token_data = token_data.update({"code": str(uuid4())})
    token = serializer.dumps(updated_token_data)
    return token


def decode_safe_token(token: str):
    try:
        return serializer.loads(token, max_age=24 * 3600)
    except Exception:
        return None