from authlib.integrations.starlette_client import OAuth
from fastapi import Request


from src.stu_house_market.core.config import settings
from src.stu_house_market.core.server_logging import app_error



oauth = OAuth()

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.GOOGLE_OAUTH2_SCREEN_CLIENT_ID,
    client_secret=settings.GOOGLE_OAUTH2_SCREEN_CLIENT_SECRET,
    client_kwargs={"scope": "openid email profile"},
)


async def google_redirect(request: Request):
    redirect_uri = request.url_for("google_oauth_callback")
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

        user_data = {
            "email": user["email"],
            "firstname": user.get("given_name"),
            "lastname": user.get("family_name"),
        }
        return user_data

    except Exception as e:
        app_error.error(f"Encouter Error with Google OAuth: {e}")
