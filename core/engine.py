"""
Тут объекты связывающие пользователя с обработчиками файла,
для получения текста страниц и генерации голоса.
"""

import os
import logging
from typing import Generator, Literal
from pathlib import Path
from core.engine_types import TextTeam, Speaker
from core.settings import SPEAKERS, READERS


log = logging.getLogger(__name__)


class Worker:
    """
    Kласс предназначенный для работы с файлом
    полученым от одного конкретного пользователя.
    reader: TextTeam  - объект для работы работы с файлом и озвучки текста.
    generator: Generator  - Объект для итерации по страницам
    """

    reader: TextTeam
    generator: Generator

    def __init__(self, reader: TextTeam, page: int = 0) -> None:
        self.reader: TextTeam = reader
        self.generator = self.reader.extract_text_from_file(num_el=page)


class Engine:
    """
    Класс связывает пользователей с обработчиками полученных файлов.
    temp_path: Path - путь к хранению временных файлов,
    speakers: dict[str, Speaker] - словарь доступных генераторов голоса,
    readers: dict[str, TextTeam] - словарь обработчиков файла
    по типу 'формат_файла' : 'обработчик',
    generators: dict[str, Worker] - словарь связывающий имя пользователя
    с обработчиком его файла 'имя_пользователя' : 'обработчик'.
    """

    temp_path: Path = Path(__file__).resolve().parent.with_name("temp")
    speakers: dict[str, Speaker] = SPEAKERS
    readers: dict[str, TextTeam] = READERS
    generators: dict[str, Worker] = {}

    def __init__(self) -> None:
        self.has_tmp_dir()

    def get_filename(self, name: str, reader: TextTeam) -> str:
        """Получаем имя+путь загруженному фаулу и путь."""

        return str(Path(self.temp_path, f"temp_{name}{reader.type}"))

    def set_worker(
        self,
        name: str,
        speaker_name: str = "pyttsx3",
        reader_name: str = "pdf",
        page: int = 0,
    ) -> bool:
        """
        Создаем связь между пользователем и обработчиком его файла.
        """

        reader: TextTeam = self.__find_reader_or_dafault(reader_name)
        speaker: Speaker = self.__find_speaker_or_dafault(speaker_name)
        path: str = self.get_filename(name, reader)
        worker = Worker(reader(path, speaker), page)
        self.generators[name] = worker
        return True

    def __find_reader_or_dafault(self, reader_name: str) -> TextTeam:
        """Ищем обработчик если не находим, берём первый."""

        reader: TextTeam = self.readers.get(reader_name)
        if not reader:
            log.debug(f"Значение {reader_name} не найдено.")
            reader = tuple(self.readers.values())[0]
        return reader

    def __find_speaker_or_dafault(self, speaker_name: str) -> Speaker:
        """Ищем обработчик если не находим, берём первый."""

        speaker: Speaker = self.speakers.get(speaker_name)
        if not speaker:
            log.debug(f"Значение {speaker_name} не найдено.")
            speaker = tuple(self.speakers.values())[1]
        return speaker

    def get_reader(self, name: str) -> TextTeam | None:
        """
        Получаем обработчик текста по имени пользователя.
        """
        gen = self.generators.get(name)
        if gen:
            log.debug(f"Ошибка получения обработчика файла для пользователя: {name}")
            return gen.reader
        return None

    def get_generator(self, name: str) -> Generator | None:
        """
        Получаем генератор по имени пользователя для итерации по документу.
        """

        gen: Worker | None = self.generators.get(name)
        if gen:
            log.debug(f"Ошибка получения генератора для пользователя: {name}")
            return gen.generator
        return None

    def has_tmp_dir(self) -> None:
        """Если нету директории temp создаём."""

        if not os.path.isdir(self.temp_path):
            os.mkdir(self.temp_path)

    def set_reader(
        self, name: str, reader_name: str, page: int = 0
    ) -> Literal[True] | None:
        """Меняем обработчик текста."""

        reader: TextTeam | None = self.readers.get(reader_name)
        worker: Worker | None = self.generators.get(name)
        if not worker or not reader:
            return None
        path: str = self.get_filename(name, reader)
        speaker: Speaker = worker.reader.get_engine.__class__
        self.generators[name] = Worker(reader(path, speaker), page)
        return True

    def set_speaker(self, name: str, speaker_name: str) -> Literal[True] | None:
        """Задаём новый генератор голоса."""

        worker: Worker | None = self.generators.get(name)
        speaker: Speaker | None = self.speakers.get(speaker_name)
        if not worker or not speaker:
            return None
        worker.reader.set_engine(speaker.__class__)
        return True
