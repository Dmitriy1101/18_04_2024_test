import os
from pathlib import Path
from unittest import TestCase
from core.voices import Speaker_gTTS, Speaker_pyttsx3

TEST_FILE = str(Path(__file__).resolve().with_name("test.mp3"))

class TestVoices(TestCase):
    """Тестируем генераторы речи."""

    test_mp3 = TEST_FILE

    def test_pyttsx3(self):
        """Тестируем гнератор голоса Speaker_pyttsx3"""

        test_obj: Speaker_pyttsx3
        self.assertIsInstance(test_obj := Speaker_pyttsx3(), Speaker_pyttsx3)
        self.assertIsNone(test_obj.save_to_file("Good day!", self.test_mp3))
        self.assertTrue(os.path.isfile(self.test_mp3))
        os.remove(self.test_mp3)

    def test_gTTS(self):
        """Тестируем гнератор голоса Speaker_gTTS"""

        test_obj: Speaker_gTTS
        self.assertIsInstance(test_obj := Speaker_gTTS(), Speaker_gTTS)
        self.assertIsNone(test_obj.save_to_file("Good day!", self.test_mp3))
        self.assertTrue(os.path.isfile(self.test_mp3))
        os.remove(self.test_mp3)

    def tearDown(self) -> None:
        """Удаляем созданый тестовый файл."""

        if os.path.isfile(self.test_mp3):
            os.remove(self.test_mp3)
        return super().tearDown()
