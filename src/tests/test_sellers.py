import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from .conftest import book_def, book2_def, seller_def, seller2_def


@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    response = await async_client.post("/api/v1/seller/", json=seller_def)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    assert result_data.get("first_name") == seller_def.get("first_name")
    assert result_data.get("last_name") == seller_def.get("last_name")
    assert result_data.get("email") == seller_def.get("email")
    assert result_data.get("password") is None

    await async_client.post("/api/v1/seller/", json=seller2_def)

    # Тест соли (одинаковые пароли не должны быть одинаковыми в БД)
    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert res[0].password != res[1].password


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller1 = sellers.Seller(**seller_def)
    seller2 = sellers.Seller(**seller2_def)
    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")
    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    assert len(result_data.get("sellers")) == 2


@pytest.mark.asyncio
async def test_get_seller_detail(db_session, async_client):
    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    book = books.Book(**book_def, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}")
    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()
    assert result_data.get("id") == seller.id
    assert result_data.get("first_name") == seller.first_name
    assert result_data.get("last_name") == seller.last_name
    assert result_data.get("email") == seller.email
    assert result_data.get("password") is None
    assert len(result_data.get("books")) == 1
    assert result_data.get("books")[0].get("id") == book.id
    assert result_data.get("books")[0].get("title") == book.title


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "John",
        "last_name": "Wick",
        "email": "boogeyman@example.com"
    }

    response = await async_client.put(f"/api/v1/seller/{seller.id}", json=data)

    assert response.status_code == status.HTTP_202_ACCEPTED

    result_data = response.json()
    assert result_data.get("id") == seller.id
    assert result_data.get("first_name") == data.get("first_name")
    assert result_data.get("last_name") == data.get("last_name")
    assert result_data.get("email") == data.get("email")
    assert result_data.get("password") is None


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    book = books.Book(**book_def, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not await db_session.get(sellers.Seller, seller.id)
    assert not await db_session.get(books.Book, book.id)
