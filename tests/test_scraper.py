import pytest
import sys
import os

# добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import get_book_data, scrape_books


# создаем фикстуру для получения данных о книге для тестов
@pytest.fixture
def one_book_data():
    """
    Фикстура для получения данных о книге для тестов
    """
    TEST_BOOK_URL = (
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    )
    return get_book_data(TEST_BOOK_URL)


# создаем фикстуру для получения данных обо всех книгах для тестов
@pytest.fixture
def all_books_data():
    """
    Фикстура для получения данных обо всех книгах для тестов
    """
    return scrape_books()


def test_get_book_data(one_book_data):
    """
    Функция, которая проверяет, что данные о книге возвращаются в виде словаря с нужными ключами
    """
    book_data = one_book_data

    # проверяем, что данные есть и это словарь
    assert book_data is not None
    assert isinstance(book_data, dict)

    # проверяем наличие всех необходимых ключей
    expected_keys = [
        "title",
        "price",
        "rating",
        "in_stock",
        "description",
        "product_info",
    ]
    for key in expected_keys:
        assert key in book_data, f"Ключ '{key}' отсутствует"


def test_get_books_count(all_books_data):
    """
    Функция, которая проверяет, что список ссылок и количество книг соответствуют ожиданиям
    """
    books_data = all_books_data

    # проверяем, что данные есть и это список
    assert books_data is not None
    assert isinstance(books_data, list)

    # проверяем, что список соответствует ожидаемому значению
    assert len(books_data) == 1000


def test_book_values(one_book_data):
    """
    Функция, которая проверяет, что значения отдельных полей корректны
    """
    book_data = one_book_data

    # проверяем конкретные значения полей
    assert book_data["title"] == "A Light in the Attic"
    assert book_data["price"] == "£51.77"
    assert book_data["rating"] == "Three"
    assert book_data["in_stock"] == "In stock (22 available)"
    assert book_data["product_info"]["UPC"] == "a897fe39b1053632"


def test_gbd_false_url():
    """
    Функция, которая проверяет, что при передаче некорректного URL get_book_data возвращает пустой словарь
    """
    false_url = "https://books.toscrape.com/catalogue/some-false-book_9999/index.html"
    result = get_book_data(false_url)

    # проверяем, что функция корректно обрабатывает некорректный URL
    assert result is not None
    assert isinstance(result, dict)


if __name__ == "__main__":
    # запуск тестов при прямом выполнении
    pytest.main([__file__])
