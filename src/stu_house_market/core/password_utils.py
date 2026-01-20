from passlib.context import CryptContext
from password_validator import PasswordValidator


pwd_context = CryptContext("bcrypt")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


schema = PasswordValidator()
schema.has(r"[a-z]+").has(r"[A-Z]+").has(r"\d+").has(r"\S").has().symbols().min(8)


def validate_password(password: str):
    return schema.validate(password)