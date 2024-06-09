"""
Тут настройки обработчиков текста, генераторов голоса и логера.
Если что-то надо добавить то это делать тут!
SPEAKERS: dict[str, Speaker] - перечислены все доступные генераторы речи
READERS: dict[str, TextTeam] - перечисленны все обработчики файлов
"""

import logging
from core.engine_types import Speaker, TextTeam
from core.speakers import PDFSpeaker
from core.voices import SpeakerGTTS, SpeakerPyttsx3


# Генераторы речи
SPEAKERS: dict[str, Speaker] = {
    "gTTS": SpeakerGTTS,
    "pyttsx3": SpeakerPyttsx3,
}
# Обработчики текстовых файлов
READERS: dict[str, TextTeam] = {
    "pdf": PDFSpeaker,
}

logging.basicConfig(
    level=logging.INFO, format="%(name)s %(asctime)s %(levelname)s %(message)s"
)
