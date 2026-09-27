import json

# импортируем внешний фреймворк для реализации обработки запросов на локальном сервере
from fastapi import FastAPI

from config import WEB_HOST, WEB_PORT
from controllers import SearchEngine, index

# создаем инстанс FastAPI
app = FastAPI()


# хенделер GET запросов на сервер
@app.get("/")
async def index_page():
    return f"Server has started. To work with search logic try sending HTTP/1.1 GET http://{WEB_HOST}:{WEB_PORT}/files/search"


# хендлер GET запросов по адресу /files/search
@app.get("/files/search")
def read_key(keyword: str | None = None, regular_search: bool | None = False) -> str:
    """Получить список файлов, содержащих заданную строку.

    :param str keyword: Ключевое слово, которое будет искаться в файлах.
    :param bool regular_search: Если True, используется простой алгоритм поиска, если False, используется алгоритм поиска через индексы.
    :return str: Список с названиями файлов, где найдено ключевое слово в формате JSON."""

    # если не введено ключевое слово
    if not keyword:
        # отображение подсказки, как ввести слово
        return f'To use the search logic, send HTTP/1.1 GET request with param "keyword", like http://{WEB_HOST}:{WEB_PORT}/files/search?keyword=helloworld'

    # создаем объекта класса
    engine = SearchEngine(keyword)

    # проверяем параметры
    if not regular_search:
        # по умолчанию используем поиск через индексы
        result = engine.index_search(index)
    else:
        # иначе используем простой поиск (реализован параллельный инпут)
        result = engine.search()

    # возвращаем результат в формате JSON
    return json.dumps(result)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host=WEB_HOST, port=WEB_PORT)
