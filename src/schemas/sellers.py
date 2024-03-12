from pydantic import BaseModel, field_validator
from email_validator import validate_email

from .books import ReturnedBook

__all__ = ["BaseSeller", "RegisteringSeller", "ReturnedSeller", "ReturnedSellerWithBooks", "ReturnedAllSellers"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str


class RegisteringSeller(BaseSeller):
    password: str
    
    @field_validator("email")
    @staticmethod
    def _validate_email(email):
        validate_email(email, check_deliverability=False)
        return email


class ReturnedSeller(BaseSeller):
    id: int


class ReturnedSellerWithBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
