"""
Тесты Обработчика файла и генераторов голоса."""
import os
from pathlib import Path
from typing import Generator
from unittest import TestCase
from core.speakers import PDFSpeaker
from core.voices import Speaker_pyttsx3, Speaker_gTTS


TEST_FILE = str(Path(__file__).resolve().with_name("test.pdf"))


class TestPDFSpeaker(TestCase):
    """Тестируем оброаботчик pdf файла."""

    def test_init_raise(self):
        """Создание экземпляка класса с ошибкой."""

        obj = PDFSpeaker
        self.assertRaises(ValueError, lambda: obj(" ", Speaker_pyttsx3))
        self.assertRaises(ValueError, lambda: obj("test.txt", Speaker_pyttsx3()))
        self.assertRaises(ValueError, lambda: obj("test.notpdf", Speaker_pyttsx3()))
        self.assertRaises(ValueError, lambda: obj("test.pdff", Speaker_pyttsx3()))
        self.assertRaises(ValueError, lambda: obj("test.json", Speaker_pyttsx3()))
        self.assertRaises(TypeError, lambda: obj("test.pdf"))
        self.assertRaises(TypeError, lambda: obj(Speaker_pyttsx3))

    def test_init_success(self):
        """Создание экземпляка класса."""

        self.assertIsInstance(PDFSpeaker(TEST_FILE, Speaker_pyttsx3), PDFSpeaker)

    def test_voices_set(self):
        """Меняем генератор голоса."""

        obj: PDFSpeaker
        self.assertIsInstance(obj := PDFSpeaker(TEST_FILE, Speaker_pyttsx3), PDFSpeaker)
        self.assertTrue(obj.set_engine(Speaker_gTTS))
        self.assertTrue(obj.set_engine(Speaker_pyttsx3))
        self.assertTrue(obj.set_engine(Speaker_pyttsx3))

    def test_save_to_file_pyttsx3(self):
        """Тестируем генерацию голоса pyttsx3"""

        obj: PDFSpeaker
        self.assertIsInstance(obj := PDFSpeaker(TEST_FILE, Speaker_pyttsx3), PDFSpeaker)
        self.assertIsInstance(obj.save_to_file("Good day sir!"), Path)
        self.assertTrue(os.path.isfile(obj.file_name_mp3))
        os.remove(obj.file_name_mp3)

    def test_save_to_file_gTTS(self):
        """Тестируем генерацию голоса gTTS"""

        obj: PDFSpeaker
        self.assertIsInstance(obj := PDFSpeaker(TEST_FILE, Speaker_gTTS), PDFSpeaker)
        self.assertIsInstance(obj.save_to_file("Good day sir!"), Path)
        self.assertTrue(os.path.isfile(obj.file_name_mp3))
        os.remove(obj.file_name_mp3)

    def test_extract_text_from_file(self):
        """Тестируем создание и работу генератора."""

        obj: PDFSpeaker
        gen: Generator
        self.assertIsInstance(obj := PDFSpeaker(TEST_FILE, Speaker_gTTS), PDFSpeaker)
        self.assertIsInstance(gen := obj.extract_text_from_file(3), Generator)
        self.assertIsInstance(next(gen), str)
        self.assertRaises(StopIteration, lambda: next(gen))
