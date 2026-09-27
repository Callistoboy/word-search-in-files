import os
import re
from collections import defaultdict

# используем многопоточность, так как для реализации более простого асинхронного
# чтения файлов понадобилась бы внешняя библиотека aiofiles
from concurrent.futures import ThreadPoolExecutor

from config import FILES_DIRECTORY


class Indexes:
    def __init__(self):
        self.files = [file for file in os.listdir(FILES_DIRECTORY)]  # alias для списка файлов

    def build(self) -> dict:
        """Создание словаря с индексами всех слов и файлами.

        :return defaultdict: Словарь, где ключом являются слова, а значениями названия файлов, где они встречаются.
        """
        word_indexes = defaultdict(list)  # модифицированный словарь

        # итерируемся по файлам
        for filename in self.files:

            file_path = os.path.join(FILES_DIRECTORY, filename)

            # открытие файлов через контекстный менеджер
            # здесь можно было сделать параллельную обработку, но потом есть сложности с объединением словарей, поэтому
            # проще сделать синхронную обработку, чем потом итерироваться по словарям в попытке объединить их
            with open(file_path, 'r', encoding='utf-8') as file:
                # приводим все к lowercase
                file_content = file.read().lower()

                # создаем набор
                words = set(file_content.split())

                # итерируемся по набору и наполняем словарь
                for word in words:

                    # очищаем слово от посторонних символов
                    _word = clear_word_from_symbols(word)

                    # добавляем в словарь
                    word_indexes[_word].append(filename)

        return word_indexes


class SearchEngine:
    def __init__(self, keyword: str):
        """Инициализация класса поисковой машины"""
        self.keyword: str = keyword.lower()  # ключевое слово
        self.filenames_list: list = [file for file in os.listdir(FILES_DIRECTORY)]  # список файлов

    def index_search(self, word_indexes: defaultdict) -> list:
        """Метод, который реализует поиск строки по файлам за O(1) за счет использования индексов.

        :param defaultdict word_indexes: Словарь с индексами всех слов.
        :return list: Список с названием файлов, которые прошли проверку на вхождение"""

        return word_indexes.get(self.keyword, [])

    def search(self) -> list:
        """Метод, который реализует параллельный поиск по файлам за O(n)

        :return list: Список с названием файлов, которые прошли проверку на вхождение"""

        # основная переменная, куда будут добавляться названия файлов
        matching_files: list = []

        # обращаемся к контекстному менеджеру из concurrent.futures для параллельной работы с файлами
        with ThreadPoolExecutor() as executor:

            # запуск функцию поиска для каждого файла из списка filenames_list (создаем фьючер)
            future_to_filename = {executor.submit(self._search_for_keyword_in_file, filename): filename for
                                  filename in self.filenames_list}

            # итерируемся по фьючерам
            for future in future_to_filename:

                # получаем результат обращаения к функции фьючера и проверяем
                # на результат (если будет строчка, вернет True)
                if future.result():
                    # добавляем в список название файла (обращаемся к словарю future_to_filename)
                    matching_files.append(future_to_filename[future])

        return matching_files

    def _search_for_keyword_in_file(self, filename: str) -> bool:
        """Производит поиск заданного слова в конкретном файле.

        Функция принимает на вход название файла, используя контекстный менеджер, открывает файл на чтение и производит
        логическую проверку вхождения указанной строки в файле. Сравнение происходит статическое.

        :param str filename: Название файла.
        :return bool: True если строчка найдена и False, если не найдена"""

        # получаем абсолютный путь к файлу
        file_path = os.path.join(FILES_DIRECTORY, filename)

        # входим в контекстный менеджер
        with open(file_path, 'r', encoding='utf-8') as file:
            # читаем данные файлы и разбиваем на слова
            file_content = file.read().lower().split()

            # возвращаем результат проверки
            return self.keyword in file_content


def clear_word_from_symbols(word: str) -> str:
    """Очистка слова от посторонних символов.

    Функция получает слово и заменяет в нем все не буквенные символы.

    :param str word: Слово, которое будет проверяться.
    :return str: Очищенное от посторонних символов слово."""

    return re.sub(r'\W', '', word)


index = Indexes().build()
