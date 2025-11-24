from pydantic import BaseModel, field_validator, Field, ConfigDict
from email_validator import validate_email
from uuid import UUID

from src.stu_house_market.utils import validate_password
from src.stu_house_market.model.user import Role


class NewUser(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str = Field(..., min_length=8)
    role: Role

    @field_validator("email")
    def validate_and_get_normalized_email(cls, value: str):
        try:
            validated_email = validate_email(value)
            return  validated_email.email
        except Exception as e:
            raise ValueError(f"Not a valid email: {e}")

    @field_validator("password")
    def check_password(cls, value: str):
        is_valid_password = validate_password(value)
        if is_valid_password:
            return value
        else:
            raise ValueError("""Not a valid password.
                             password must contain at least one lowercase letter, 
                             one uppercase letter, a number, a symbol and no space""")
        
class User(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    email: str
    role: Role

    model_config = ConfigDict(from_attributes=True)

class UserCreated(BaseModel):
    message: str
    user: User

class UserLogin(BaseModel):
    message: str
    user: User
    access_token: str
    refresh_token : str
    token_type: str

    model_config = ConfigDict(from_attributes=True)




