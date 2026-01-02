from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from src.stu_house_market.core.config import settings

oauth = OAuth()

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.GOOGLE_OAUTH2_SCREEN_CLIENT_ID,
    client_secret=settings.GOOGLE_OAUTH2_SCREEN_CLIENT_SECRET,
    client_kwargs={"scope": "openid email profile"},
)


async def google_redirect(request: Request):
    redirect_uri = request.url_for("validate_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def google_callback(request: Request):
    try:
        
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        if not user:
            resp = await oauth.google.get(
                "https://openidconnect.googleapis.com/v1/userinfo", token=token
            )
            user = resp.json()

            """
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[Role] = mapped_column(PQ_ENUM(Role, name="role_enum"), nullable=False)

"""
            
        return user

    except Exception as e:
        print(f"Google OAuth error: {e}")
        return None
    
