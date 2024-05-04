"""
Обработчик текста.
"""
import PyPDF2
from pathlib import Path
from typing import Generator
from pyttsx3.engine import Engine
from abc import ABC, abstractmethod
from core.engine_types import Speaker
from core.log_settings import get_logger


log = get_logger(__name__)


class TextSpeakerABC(ABC):
    """
    __file_type: задаёт тип рабочих файлов например '.pdf'
    """

    __file_type: str

    def __init__(self, file_name_path: str, speaker: Speaker) -> None:
        self.init(file_name_path, speaker)

    def init(self, file_name_path: str, speaker: Speaker) -> None:
        if not self.set_path_file(file_name_path):
            raise ValueError(
                "Невозможно создать файл с таким именем по данному пути,\nубедитесь что путь существует"
            )
        if not self.set_engine(speaker):
            raise ValueError("Невозможно создать объект озвучки текста.")

    def is_my_file_name(self, file_name: str) -> bool:
        """Вернёт True если это имя pdf файла, или выбросит ошибку"""

        if not file_name[-4:] == self.type or len(file_name) < 5:
            log.debug("Ошибка типа файла чтения.")
            raise NameError(f"{file_name} <- Не имя {self.type[1:]} файла")
        return True

    def is_mp3_file_name(self, file_name: str) -> bool:
        """Вернёт True если это имя mp3 файла, или выбросит ошибку"""

        if not file_name[-4:] == ".mp3" or len(file_name) < 5:
            log.debug("Ошибка типа файла озвучки.")
            raise NameError(f"{file_name} <- Не имя mp3 файла")
        return True

    def set_path_file(self, path_to_file: str) -> bool:
        """Задаём пути к рабочему файлу"""

        self.path: Path = Path(__file__).resolve().parent
        self.set_path_my_file(path_to_file=path_to_file)
        mp3_file: str = path_to_file.replace(self.type, ".mp3")
        self.set_path_mp3_file(path_to_file=mp3_file)
        return True

    def set_path_my_file(self, path_to_file: str) -> bool:
        """зыдаём путь к рабочему pdf файлу"""

        self.is_my_file_name(file_name=path_to_file)
        self.file_name: Path = Path(self.path, path_to_file)
        return True

    def set_path_mp3_file(self, path_to_file: str) -> bool:
        """зыдаём путь к рабочему mp3 файлу"""

        self.is_mp3_file_name(file_name=path_to_file)
        self.file_name_mp3: Path = Path(self.path, path_to_file)
        return True

    @classmethod
    @property
    def type(cls):
        return getattr(cls, f"_{cls.__name__}__file_type")

    @property
    def get_engine(self) -> Engine:
        """Получаем обект озвучки."""
        return self._engine

    @abstractmethod
    def save_to_file(self, text: str):
        pass

    @abstractmethod
    def set_engine(self) -> bool:
        pass

    @abstractmethod
    def extract_text_from_file(self, num_el: int = 0) -> Generator:
        pass

    @abstractmethod
    def get_tmp_filename(name: str) -> str:
        pass


class PDFSpeaker(TextSpeakerABC):
    """
    Преобрразуем PDF книгу в озвученый текст.
    При инициализации передай путь к файлу.
    """

    __file_type: str = ".pdf"

    def __init__(self, file_name_path: str, speaker: Speaker) -> None:
        self.init(file_name_path, speaker)

    def extract_text_from_file(self, num_el: int = 0) -> Generator:
        """
        Генератор для итерации по страницам.
        Возвращает текст страницы.
        Может принимать номер страницы начала.
        """

        log.info(f"Создаём генератор для чтения документа {self.file_name}")
        with open(self.file_name, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in reader.pages[num_el:]:
                text = page_num.extract_text()
                if not text:
                    num_el += 1
                    continue
                yield f"Страница {num_el} \n {text}"
                num_el += 1

    def set_engine(self, speaker: Speaker, *args, **kwargs) -> bool:
        """Создаём объект озвучки на основе pyttsx3, и задаём скорость озвучки."""

        try:
            self._engine = speaker(*args, **kwargs)
        except Exception as e:
            log.exception(
                "Невозможно получить  объект озвучки на основе pyttsx3.",
                exc_info=False,
                extra={"Exception": e},
            )
            return False
        return True

    def save_to_file(self, text):
        self.get_engine.save_to_file(
            text=text,
            file_name=str(self.file_name_mp3),
        )

    def get_tmp_filename(name: str) -> str:
        """Задаём имя загруженному фаулу."""

        return f"temp_{name}.pdf"
