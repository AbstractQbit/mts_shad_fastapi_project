from pydantic import BaseModel, field_validator
from email_validator import validate_email

class SellerCredentials(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @staticmethod
    def _validate_email(email):
        validate_email(email, check_deliverability=False)
        return email


class ReturnedToken(BaseModel):
    access_token: str
    token_type: str
