"""
Объекты генераторов речи.
"""

import logging
from abc import ABC, abstractmethod
import pyttsx3
from gtts import gTTS


log = logging.getLogger(__name__)


class SpeakersABC(ABC):
    """Абстрактный класс для генераторов голоса."""

    _name: str  # module use

    @abstractmethod
    def __init__(self) -> None:
        log.debug("Создаём генератор голоса: %s", self._name)

    def __repr__(self) -> str:
        return f"name: {self.__class__.__name__}, module use: {self._name}"

    def __str__(self) -> str:
        return f"name: {self.__class__.__name__}, module use: {self._name}"

    @abstractmethod
    def save_to_file(self, text: str, file_name: str):
        """Тут мы преобразуем текст в голос и сохраняем в файл."""


class SpeakerPyttsx3(SpeakersABC):
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


class SpeakerGTTS(SpeakersABC):
    """
    Используем Google для озвучки.
    """

    _name: str = "gTTS"

    def save_to_file(self, text: str, file_name: str):
        speaker = gTTS(text, lang="ru")
        speaker.save(file_name)
