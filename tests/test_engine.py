import os
import shutil
from pathlib import Path
from unittest import TestCase
from core.engine import Engine, Worker
from typing import Generator
from core.speakers import PDFSpeaker
from tests.test_speakers import TEST_FILE
from main import get_filename

TEST_USER = "test_user"


class TestEngine(TestCase):
    """Тестируем обрабработчик файлов пользователей."""

    eng: Engine

    def setUp(self) -> None:
        """
        Тестируем создание обработчика, далее работаем только с ним
        и создаём тестовый файл для тестов его работы.
        Тестовый файл будет скопирован из образца расположенного
        в tests и с именем TEST_FILE, используя TEST_USER
        в качестве тестового пользователя.
        """
        eng: Engine
        self.assertIsInstance(eng := Engine(), Engine)
        self.assertTrue(os.path.isdir(eng.temp_path))
        self.eng = eng
        self.assertTrue(self.eng.set_worker(TEST_USER))
        self.test_file: Path = self.eng.generators[TEST_USER].reader.file_name
        shutil.copy(TEST_FILE, self.test_file)
        return super().setUp()

    def test_get_reader(self):
        """Тестируем извлечение обработчика текста по имени пользователя."""

        self.assertIsInstance(self.eng.get_reader(TEST_USER), PDFSpeaker)
        self.assertIsNone(self.eng.get_reader("name"))
        self.assertIsNone(self.eng.get_reader(None))

    def test_get_worker(self):
        """Тестируем извлечение генератора по имени пользователя."""

        self.assertIsInstance(self.eng.get_worker(TEST_USER), Worker)
        self.assertRaises(KeyError, lambda: self.eng.get_worker("name"))
        self.assertRaises(KeyError, lambda: self.eng.get_worker(1))
        self.assertRaises(KeyError, lambda: self.eng.get_worker(None))

    def test_set_reader(self):
        """Тестируем смену обработчика файла."""

        self.assertTrue(self.eng.set_reader(TEST_USER, "pdf"))
        self.assertFalse(self.eng.set_reader(TEST_USER, "name"))
        self.assertFalse(self.eng.set_reader(TEST_USER, None))

    def test_set_speaker(self):
        """Тестируем изменение генератора голоса."""

        self.assertTrue(self.eng.set_speaker(TEST_USER, "gTTS"))
        self.assertFalse(self.eng.set_speaker(TEST_USER, "name"))
        self.assertFalse(self.eng.set_speaker(TEST_USER, None))

    def tearDown(self) -> None:
        """Удаляем созданый тестовый файл."""

        os.remove(self.test_file)
        return super().tearDown()
