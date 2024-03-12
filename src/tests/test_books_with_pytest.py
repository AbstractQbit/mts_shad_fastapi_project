import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from .conftest import book_def, book2_def, seller_def


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    data = {
        "title": "Wrong Code",
        "author": "Robert Martin",
        "pages": 104,
        "year": 2007,
        "seller_id": seller.id,
    }
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 1,
        "title": "Wrong Code",
        "author": "Robert Martin",
        "count_pages": 104,
        "year": 2007,
        "seller_id": seller.id,
    }


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    book1 = books.Book(**book_def, seller_id=seller.id)
    book2 = books.Book(**book2_def, seller_id=seller.id)
    db_session.add_all([book1, book2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert (
        len(response.json()["books"]) == 2
    )  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {
                **book_def,
                "id": book1.id,
                "seller_id": seller.id,
            },
            {
                **book2_def,
                "id": book2.id,
                "seller_id": seller.id,
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    book1 = books.Book(**book_def, seller_id=seller.id)
    book2 = books.Book(**book2_def, seller_id=seller.id)
    db_session.add_all([book1, book2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 1823,
        "count_pages": 240,
        "id": book1.id,
        "seller_id": seller.id,
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    book = books.Book(**book_def, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    seller = sellers.Seller(**seller_def)
    db_session.add(seller)
    await db_session.flush()

    book = books.Book(**book_def, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={
            "title": "Mziri",
            "author": "Lermontov",
            "count_pages": 100,
            "year": 2007,
            "id": book.id,
            "seller_id": seller.id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books.Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.id == book.id
