import time
import requests
import schedule
from bs4 import BeautifulSoup


def get_book_data(book_url: str) -> dict:
    """
    Извлекает данные о книге с веб-страницы.

    Args:
        book_url (str): URL-адрес страницы с информацией о книге

    Returns:
        dict: словарь с данными о книге:
            title (str): название книги
            price (str): цена книги
            rating (str): рейтинг книги
            in_stock (str): информация о наличии
            description (str): описани книги
            product_info (dict): дополнительные характеристики из таблицы Product Information
    Raises:
        requests.RequestException: если ошибка при запросе к веб-странице
    """

    result = {}
    session = requests.Session()

    try:
        # устанавливаем соединение с сайтом
        response = session.get(book_url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # извлекаем информацию и обрабатываем ситуацию, когда какого-либо значения нет

        # извлекаем название книги
        title = soup.find("h1")
        result["title"] = title.text.strip() if title else ""

        # извлекаем цену и обрабатываем неизвестный символ в цене
        price = soup.find(class_="price_color")
        result["price"] = price.text.strip().replace("Â", "") if price else ""

        # извлекаем рейтинг
        rating_elem = soup.find(class_="star-rating")
        if rating_elem:
            classes = rating_elem.get("class")
            # оставляем только класс, соответствующий рейтингу
            rating_class = [cls for cls in classes if cls != "star-rating"]
            result["rating"] = rating_class[0] if rating_class else ""
        else:
            result["rating"] = ""

        # извлекаем информацию о наличию книги на складе
        in_stock = soup.find(class_="instock availability")
        result["in_stock"] = in_stock.text.strip() if in_stock else ""

        # извлекаем описание книги
        desc_div = soup.find("div", id="product_description")
        if desc_div:
            desc_par = desc_div.find_next_sibling("p")
            result["description"] = desc_par.text.strip() if desc_par else ""
        else:
            result["description"] = ""

        # извлекаем дополнительную информацию о книге из таблицы Product Information
        table = soup.find("table", class_="table-striped")
        product_info = {}

        if table:
            # извлекаем ряды
            rows = table.find_all("tr")
            for row in rows:
                # извлекаем "заголовки" и "значения"
                header = row.find("th")
                value = row.find("td")
                if header and value:
                    header_text = header.text.strip()
                    value_text = value.text.strip()
                    # обрабатываем неизвестный символ в ценах
                    if "Price" in header_text or "Tax" in header_text:
                        value_text = value_text.replace("Â", "")
                    product_info[header_text] = value_text

        result["product_info"] = product_info
        return result

    except requests.RequestException as e:
        print(f"Ошибка {e} при запросе к {book_url}")
        return {}


def scrape_books(base_url="http://books.toscrape.com/", is_save=False):
    """
    Проходится по всем страницам из каталога на веб-странице,
    осуществляет парсинг всех страниц с помощью get_book_data().

    Args:
        base_url (str): базовый URL для сайта. По умолчанию 'http://books.toscrape.com/'
        is_save (bool): если True - сохраняет результат в файл artifacts/books_data.txt

    Returns:
        list: список словарей с данными о книгах
    """

    all_books_result = []
    page_num = 1
    # создаем сессии для обработки большого кол-ва запросов
    session = requests.Session()

    # цикл для прохода по каталогам с главной страницы
    while True:
        # создаем "конструктор" адреса каталога
        catalogue_url = f"{base_url}catalogue/page-{page_num}.html"

        # устанавливаем соединение с сайтом
        response = session.get(catalogue_url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # ищем элементы с информацией о книгах
        books_articles = soup.find_all("article", class_="product_pod")
        # если больше нет - конец каталога, выходим
        if not books_articles:
            break

        # обрабатываем каждую книгу на странице
        for book_article in books_articles:
            # ищем ссылку на страницу с информацией о книге
            link_tag = book_article.find("h3").find("a")
            if link_tag and link_tag.get("href"):
                # относительный URl адрес страницы книги
                book_relative_url = link_tag["href"]

                # обработка URL
                if not book_relative_url.startswith("catalogue/"):
                    book_relative_url = "catalogue/" + book_relative_url
                book_url = base_url + book_relative_url

                # получаем данные о книги с помощью get_book_data()
                try:
                    book_data = get_book_data(book_url)
                    if book_data and book_data.get("title"):
                        all_books_result.append(book_data)

                except Exception as e:
                    print(f"Ошибка {e} при обработке книги")
                    continue

        # проверяем наличие перехода на следующую страницу
        # если нет - значит это последняя страница
        next_li = soup.find("li", class_="next")
        if not next_li:
            break

        # увеличиваем номер страницы
        page_num += 1
        # задержка, чтобы не перегрузить сервер
        time.sleep(0.5)

    # сохраняем информацию в файл, если передан флаг is_save=True
    if is_save and all_books_result:
        # открываем файл и записываем
        with open("artifacts/books_data.txt", "w", encoding="utf-8") as f:
            # заголовок
            f.write(f"Обработано {len(all_books_result)} книг\n")
            # линия отделения заголовка от остального текста
            f.write(f'{"=" * 60}\n\n')

            # обрабатываем каждую книгу
            for i, book in enumerate(all_books_result, 1):
                f.write(f"Книга № {i}\n")
                f.write(f"Название: {book.get('title', ' ')}\n")
                f.write(f"Цена: {book.get('price', ' ')}\n")
                f.write(f"Рейтинг: {book.get('rating', ' ')}\n")
                f.write(f"В наличии: {book.get('in_stock', ' ')}\n")
                f.write(f"Описание: {book.get('description', ' ')}\n")
                # обрабатываем доп. информацию о книге
                product_info = book.get("product_info", {})
                if product_info:
                    f.write(f"Дополнительная информация:\n")
                    for key, value in product_info.items():
                        f.write(f"{key}: {value}\n")

                # добавляем разделитель между книгами
                if i < len(all_books_result):
                    f.write(f'\n{"-" * 40}\n\n')

    return all_books_result


def scheduler_setup():
    """
    Основная функция для настройки планировщика.

    Настраивает планировщик для ежедневного вызова функции schedule_function() в 19:00.
    Запускает бесконечный цикл для проверки запланированных задач.
    Останавливается при получении KeyboardInterrupt (ручная остановка Ctrl+C).
    """

    def schedule_function():
        """
        Функция для планировщика, которая вызывает scrape_books() ежедневно в 19:00.

        Вызывает функцию scrape_books() с параметром is_save=True, которая сохраняет результат в файл.
        """

        current_time = time.strftime("%H:%M")
        print(f"Автозапуск функции сбора данных о книгах в {current_time} начат!")

        try:
            scrape_books(is_save=True)
            print(f"Выполнение функции завершено в {time.strftime("%H:%M")}!")
        except Exception as e:
            print(f"Ошибка при выполнении функции: {e}")

        print("Следующий запуск завтра в 19:00.")

    # удаляем предыдущие "задания"
    schedule.clear()

    # настраиваем выполнение каждый день в 19.00
    schedule.every().day.at("19:00").do(schedule_function)

    print("Планировщик запущен. Ожидайте 19:00.")
    print("Нажмите Ctrl+C или Interrupt the kernel для остановки.")

    try:
        while True:
            # проверяем, есть ли задачи
            schedule.run_pending()
            # ждем 60 сек перед следующей проверкой
            time.sleep(60)
    except KeyboardInterrupt:
        print(
            "Планировщик остановлен вручную.\nРаботоспособность кода проверена успешно!"
        )
