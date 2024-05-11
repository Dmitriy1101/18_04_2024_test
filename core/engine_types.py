from typing import Generator, Protocol
from pathlib import Path


class Speaker(Protocol):
    def save_to_file(text: str, file_name: str):
        ...


class TextTeam(Protocol):
    file_name: Path = ...
    file_name_mp3: Path = ...

    def __init__(file_name_path: str, speaker: Speaker) -> None:
        ...

    def get_engine() -> Speaker:
        ...

    def set_engine(speaker: Speaker):
        ...

    def extract_text_from_file(num_el: int) -> Generator:
        ...

    def save_to_file(text: str):
        ...

    @classmethod
    @property
    def type() -> str:
        ...
