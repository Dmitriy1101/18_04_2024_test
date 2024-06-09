"""
Тут объекты связывающие пользователя с обработчиками файла,
для получения текста страниц и генерации голоса.
"""

import os
import logging
from typing import Generator, Literal, Self
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
        self.__page: int = page

    def __getitem__(self, num_el: int) -> Path:
        return self.reader[num_el]

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Path:
        if 0 <= self.page <= len(self.reader):
            v: Path = self.reader[self.page]
            self.page = self.page + 1
            return v
        raise StopIteration

    def set_speaker(self, speaker: Speaker) -> bool:
        """Set new voice generator"""
        return self.reader.set_engine(speaker)

    @property
    def page(self) -> int:
        """Page of text"""
        return self.__page

    @page.setter
    def page(self, page: int) -> Literal[True]:
        self.__page = page
        return True


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

        reader: TextTeam | None = self.readers.get(reader_name)
        if not reader:
            log.debug("Значение %s не найдено.", reader_name)
            reader = tuple(self.readers.values())[0]
        return reader

    def __find_speaker_or_dafault(self, speaker_name: str) -> Speaker:
        """Ищем обработчик если не находим, берём первый."""

        speaker: Speaker | None = self.speakers.get(speaker_name)
        if not speaker:
            log.debug("Значение %s не найдено.", speaker_name)
            speaker = tuple(self.speakers.values())[1]
        return speaker

    def get_reader(self, name: str) -> TextTeam | None:
        """
        Получаем обработчик текста по имени пользователя.
        """
        gen = self.generators.get(name)
        if gen:
            log.debug("Ошибка получения обработчика файла для пользователя: %s", name)
            return gen.reader
        return None

    def has_tmp_dir(self) -> None:
        """Если нету директории temp создаём."""

        if not os.path.isdir(self.temp_path):
            os.mkdir(self.temp_path)

    def set_reader(self, name: str, reader_name: str, page: int = 0) -> bool:
        """Меняем обработчик текста."""

        reader: TextTeam | None = self.readers.get(reader_name)
        worker: Worker | None = self.generators.get(name)
        if not worker or not reader:
            log.debug(
                "Обработчик пользователя: %s, не смог изменить обработчик текста на: %s",
                name,
                reader_name,
            )
            return False
        path: str = self.get_filename(name, reader)
        speaker = worker.reader.get_engine.__class__
        self.generators[name] = Worker(reader(path, speaker), page)
        return True

    def set_speaker(self, name: str, speaker_name: str) -> bool:
        """Задаём новый генератор голоса."""

        worker: Worker | None = self.generators.get(name)
        speaker: Speaker | None = self.speakers.get(speaker_name)
        if not worker or not speaker:
            log.debug(
                "Обработчик пользователя: %s не смог изменить генератор голоса на: %s",
                name,
                speaker_name,
            )
            return False
        worker.set_speaker(speaker)
        return True

    def get_worker(self, name: str) -> Worker:
        """
        Получаем генератор по имени пользователя для итерации по документу.
        """

        return self.generators[name]
