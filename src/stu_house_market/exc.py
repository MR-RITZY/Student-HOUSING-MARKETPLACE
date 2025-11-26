from fastapi import HTTPException, Request, FastAPI
from fastapi.responses import JSONResponse


async def user_already_exists(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "User Already Exists", "detail": exc.detail},
    )


class UserAlreadyExistsException(HTTPException):
    pass


async def user_not_found(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "User Not Found", "detail": exc.detail},
    )


class UserNotFoundException(HTTPException):
    pass


async def invalid_credentials(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Invalid Credentials", "detail": exc.detail},
    )


class InvalidCredentialsException(HTTPException):
    pass

async def invalid_token(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Invalid or Expired Token", "detail": exc.detail},
    )


class InvalidTokenException(HTTPException):
    pass


async def unverified_user(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Not A Verified User", "detail": exc.detail},
    )


class UnverifiedUserException(HTTPException):
    pass


def register_exceptions(app: FastAPI):
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists)
    app.add_exception_handler(UserNotFoundException, user_not_found)
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials)
    app.add_exception_handler(InvalidTokenException, invalid_token)
    app.add_exception_handler(UnverifiedUserException, unverified_user)