# ДЗ 3. Система для автоматического сбора и парсинга данных о книгах с сайта [Books to Scrape](https://books.toscrape.com/).

Этот проект представляет собой веб-скрейпер для сайта [Books to Scrape](https://books.toscrape.com/).

## Цель

Сбор подробной информации обо всех книгах в каталоге, включая название, цену, рейтинг, наличие, описание и др.

## Структура проекта

```
  books_scraper/
  ├── artifacts/
  │   └── books_data.txt
  ├── notebooks/
  │   └── Неяскина_HW_03_python_ds_2025.ipynb
  ├── scraper.py
  ├── README.md
  ├── tests/
  │   └── test_scraper.py
  ├── .gitignore
  └── requirements.txt
```

## Основные возможности

`scraper.py` - основной скрипт для сбора данных

- Парсинг данных отдельной книги (`get_book_data`).
- Обход всех страниц каталога и сбор данных со всех книг (`scrape_books`).
- Сохранение результатов в файл `artifacts/books_data.txt`.
- Автоматический ежедневный запуск парсера в 19:00 с использованием `schedule`.

## Инструкции по запуску

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/friemari/mipt_python_hw3.git
   ```

2. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Для запуска тестов:

   ```bash
   pytest tests/test_scraper.py
   ```

5. Для запуска парсера в режиме планировщика (ежедневный запуск в 19:00):
   ```bash
   python scraper.py
   ```

## Используемые библиотеки

- `requests`
- `beautifulsoup4`
- `schedule`
- `pytest`
