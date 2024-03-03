import argon2
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import mintJWT
from src.configurations.database import get_async_session
from src.schemas.auth import SellerCredentials, ReturnedToken
from src.models.sellers import Seller

token_router = APIRouter(tags=["token"], prefix="/token")

DBSession = Depends(get_async_session)

hasher = argon2.PasswordHasher()


@token_router.post("/", response_model=ReturnedToken, status_code=status.HTTP_200_OK)
async def get_token(
    credentials: SellerCredentials,
    session: AsyncSession = DBSession,
):
    seller = await session.execute(select(Seller).where(Seller.email == credentials.email))
    seller = seller.scalars().first()

    if not seller:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        hasher.verify(seller.password, credentials.password)
    except argon2.exceptions.VerifyMismatchError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    token = mintJWT(seller.id, {"email": seller.email})

    return {"access_token": token, "token_type": "bearer"}
