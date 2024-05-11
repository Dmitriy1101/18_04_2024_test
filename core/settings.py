"""
Тут настройки обработчиков текста, генераторов голоса и логера.
Если что-то надо добавить то это делать тут!
SPEAKERS: dict[str, Speaker] - перечислены все доступные генераторы речи
READERS: dict[str, TextTeam] - перечисленны все обработчики файлов
"""
from core.engine_types import *
from core.speakers import PDFSpeaker
from core.voices import Speaker_gTTS, Speaker_pyttsx3
import logging


SPEAKERS: dict[str, Speaker] = {
    "gTTS": Speaker_gTTS,
    "pyttsx3": Speaker_pyttsx3,
}

READERS: dict[str, TextTeam] = {
    "pdf": PDFSpeaker,
}

logging.basicConfig(
    level=logging.INFO, format="%(name)s %(asctime)s %(levelname)s %(message)s"
)