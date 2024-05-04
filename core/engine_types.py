from typing import Generator, Protocol


class Speaker(Protocol):
    def save_to_file(text: str, file_name: str):
        ...


class TextTeam(Protocol):
    def __init__(file_name_path: str, speaker: Speaker) -> None:
        ...

    def get_engine():
        ...

    def set_engine(speaker: Speaker):
        ...

    def extract_text_from_file(num_el: int) -> Generator:
        ...

    def save_to_file(text: str):
        ...

    @classmethod
    @property
    def type():
        ...
