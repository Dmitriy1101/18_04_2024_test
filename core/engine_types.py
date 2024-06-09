"""
Типы генераторов голоса и обработчиков текста.
"""

from typing import Generator, Protocol
from pathlib import Path


class Speaker(Protocol):
    """Генераторы голоса."""

    def save_to_file(self, text: str, file_name: str):
        ...


class TextTeam(Protocol):
    """Обработчики текстовых файлов."""

    file_name: Path
    file_name_mp3: Path

    def __init__(self, file_name_path: str, speaker: Speaker) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, num_el: int) -> Path:
        ...

    def get_engine(self) -> Speaker:
        ...

    def set_engine(self, speaker: Speaker, *args, **kwargs) -> bool:
        ...

    def extract_text_from_file(self, num_el: int) -> Generator:
        ...

    def save_to_file(self, text: str):
        ...

    @classmethod
    @property
    def type(cls) -> str:
        ...
