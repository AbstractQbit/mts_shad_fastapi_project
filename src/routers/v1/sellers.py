from typing import Annotated

import argon2
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import (
    BaseSeller,
    RegisteringSeller,
    ReturnedAllSellers,
    ReturnedSeller,
    ReturnedSellerWithBooks,
)

seller_router = APIRouter(tags=["seller"], prefix="/seller")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

hasher = argon2.PasswordHasher()


@seller_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)
async def create_seller(seller: RegisteringSeller, session: DBSession):
    seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=hasher.hash(seller.password),
    )
    session.add(seller)
    await session.flush()
    return seller


@seller_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


@seller_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession):
    # res = await session.get(Seller, seller_id, options=[selectinload(Seller.books)])
    res = await session.scalar(
        select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
    )
    return res


@seller_router.put(
    "/{seller_id}", response_model=ReturnedSeller, status_code=status.HTTP_202_ACCEPTED
)
async def update_seller(seller_id: int, seller: BaseSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = seller.first_name
        updated_seller.last_name = seller.last_name
        updated_seller.email = seller.email
        await session.flush()
        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@seller_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)
        await session.flush()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_404_NOT_FOUND)
