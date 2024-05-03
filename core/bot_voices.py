import pyttsx3
from gtts import gTTS
from abc import ABC, abstractmethod
from core.bot_settings import get_logger

log = get_logger(__name__)


class SpeakersABC(ABC):
    _name: str

    def __str__(self) -> str:
        return self._name

    @abstractmethod
    def __init__(self) -> None:
        log.debug(f"Создаём генератор голоса: {self._name}")

    @abstractmethod
    def save_to_file(self, text: str, file_name: str):
        """Тут мы преобразуем текст в голос и сохраняем в файл."""
        pass


class Speaker_pyttsx3(SpeakersABC):
    """Озвучка голосом Windows диктора."""

    _name: str = "pyttsx3"

    def __init__(self, speed: int = 125) -> None:
        super().__init__()
        self.__engine = pyttsx3.init()
        self.__engine.setProperty("rate", speed)

    def save_to_file(self, text: str, file_name: str):
        self.__engine.save_to_file(
            text=text,
            filename=file_name,
        )
        self.__engine.runAndWait()


class Speaker_gTTS(SpeakersABC):
    """
    Используем Google для озвучки.
    """

    _name: str = "pyttsx3"

    def __init__(self) -> None:
        super().__init__()

    def save_to_file(self, text: str, file_name: str):
        speaker = gTTS(text, lang="ru")
        speaker.save(file_name)
