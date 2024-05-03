"""
Тут инициализированы все генераторы речи 
и обработчики текста.
"""
import logging
from core.bot_dataclass import *
from core.bot_speaker import PDFSpeaker
from core.bot_voices import Speaker_gTTS, Speaker_pyttsx3


SPEAKERS = SpeakersTeam()
SPEAKERS.speakers = {
    "gTTS": Speaker_gTTS,
    "pyttsx3": Speaker_pyttsx3,
}

READERS = ReadersTeam()
READERS.readers = {
    "pdf": PDFSpeaker,
}

GENERATORS = GeneratorsTeam()
GENERATORS.speakers = SPEAKERS
GENERATORS.readers = READERS

logging.basicConfig(
    level=logging.INFO, format="%(name)s %(asctime)s %(levelname)s %(message)s"
)


def get_logger(name) -> logging.Logger:
    '''Получаем настроеный логер.'''
    return logging.getLogger(name)
