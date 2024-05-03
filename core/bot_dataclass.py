"""
Скоро!
"""
from typing import Generator
from pathlib import Path
from core.bot_types import TextTeam, Speaker


class SpeakersTeam:
    """Набор генераторов речи."""

    speakers: dict[str, Speaker]

    def get_speaker(self, name: str) -> Speaker | None:
        return self.speakers.get(name)


class ReadersTeam:
    """Набор обработчиков текста."""

    readers: dict[str, TextTeam]

    def get_reader(self, name: str) -> TextTeam | None:
        return self.readers.get(name)


class Worker:
    """
    Датакласс обработчика текста.
    Упрощает доступ к объектам обработки.
    reader: TextTeam - объект управления озвучкой текыта в файл
    generator: Generator -Генератор для итерации по тексту.
    """

    reader: TextTeam
    generator: Generator

    def __init__(self, reader: TextTeam, page: int = 0) -> None:
        self.reader: TextTeam = reader
        self.generator = self.reader.extract_text_from_file(num_el=page)


class GeneratorsTeam:
    """
    Датакласс генераторов озвучки и обработки текста.
    Связывает пользователя с обработчиком его файла
    и запросов к файлу.
    """

    temp_path: Path = Path(__file__).resolve().parent.with_name("temp")
    speakers: SpeakersTeam
    readers: ReadersTeam
    generators: dict[str, Worker] = {}

    def get_filename(self, name: str, reader: TextTeam) -> str:
        """Задаём имя+путь загруженному фаулу и путь."""

        return str(Path(self.temp_path, f"temp_{name}{reader._file_type}"))

    def set_genegator(
        self,
        name: str,
        speaker_name: str = "pyttsx3",
        reader_name: str = "pdf",
        page: int = 0,
    ) -> bool:
        """
        Создаем связь между пользователем и обработчиком его файла.
        """

        reader: TextTeam = self.readers.get_reader(name=reader_name)
        speaker: Speaker = self.speakers.get_speaker(name=speaker_name)
        path: str = self.get_filename(name, reader)
        print(f"path : {path}")
        worker = Worker(reader(path, speaker), page)
        self.generators[name] = worker
        return True

    def get_reader(self, name) -> TextTeam | None:
        """
        Получаем обработчик текста по имени пользователя.
        """
        gen = self.generators.get(name)
        if gen:
            return gen.reader
        return None

    def get_generator(self, name: str) -> Generator | None:
        """
        Получаем генератор для итерации по документу
        , по имени пользователя.
        """

        gen = self.generators.get(name)
        if gen:
            return gen.generator
        return None
