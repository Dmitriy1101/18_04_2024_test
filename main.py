from typing import Generator
import telebot
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telebot import types
from core.engine import Engine
from core.speakers import PDFSpeaker


# Извлекаем токен в окружение
load_dotenv()

# Инициализация Telegram бота
TOKEN: str = os.environ.get("speaker_bot")
bot = telebot.TeleBot(TOKEN)

log = logging.getLogger(__name__)
# Обработчики файлов.
GENERATORS = Engine()

button_menu = types.KeyboardButton("Домой")
button_download_pdf = types.KeyboardButton("Загрузить PDF файл")
button_use_old = types.KeyboardButton("Использовать загруженый файл")
button_start_page = types.KeyboardButton("С начала")
button_next = types.KeyboardButton("Следующая страница")


def get_filename(message: types.Message) -> str:
    """Задаём имя загруженному фаулу."""

    return f"temp_{message.chat.username}.pdf"


def get_file(file_name: str) -> bool:
    """Ищем сохраненный файл."""

    return os.path.isfile(Path(GENERATORS.temp_path, file_name))


@bot.message_handler(commands=["start", "Домой", "H", "Д"])
def send_welcome(message: types.Message):
    """Обработчик команды start"""

    log.info("Приперся тут один.", extra={message.chat.id: message.chat.username})
    bot.send_message(message.chat.id, "Привет! Я озвучиваю PDF книги")
    menu(message)


@bot.message_handler(content_types=["text"])
def keyboard_actions(message: types.Message):
    """
    Метод обработки текста сообщений вне контекста прошлых действий.
    """

    if message.text.lower() == "загрузить pdf файл":
        bot.send_message(message.chat.id, "Отправьте PDF файл.")
    elif message.text.lower() == "домой":
        menu(message)
    elif message.text == "Использовать загруженый файл":
        bot.send_message(message.chat.id, "Принято.")
        start_read(message)


def menu(message: types.Message):
    """Главное меню бота."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buts: list[types.KeyboardButton] = []
    buts.append(button_download_pdf)

    if get_file(get_filename(message)):
        buts.append(button_use_old)
    bot.send_message(
        message.chat.id,
        "Отправь мне прикреплённый PDF файл, я могу озвучить его текст. \
            \nЕсли я найду старый файл мы можем прослушать его.",
        reply_markup=markup.row(*buts),
    )
    bot.register_next_step_handler(message, got_it)


def got_it(message: types.Message):
    """
    Обработка выбора сделанного на стартовое сообщение,
    в случае неверной комманды вернёт назад.
    """

    if message.text == "Загрузить PDF файл":
        bot.send_message(message.chat.id, "Отправьте PDF файл.")
    elif message.text == "Использовать загруженый файл":
        bot.send_message(message.chat.id, "Принято.")
        start_read(message)
    else:
        bot.reply_to("Возникли проблемы с вашими руками!")
        menu(message)


def start_read(message: types.Message):
    """Спрашиваем начальную страницу чтения."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(button_start_page, button_menu)
    bot.send_message(
        message.chat.id,
        "Читаем с начала? Или введи номер страницы.",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, get_psge)


def get_psge(message: types.Message):
    """Узнаём страницу с которой читаемю"""

    if message.text == button_start_page.text:
        create_gen(message)
    elif message.text == button_menu.text:
        menu(message)
    elif message.text.isdigit():
        create_gen(message, page=int(message.text))
    else:
        bot.reply_to("Возникли проблемы с вашими руками!")
        start_read(message)


def get_mp3_filename(message: types.Message) -> str:
    """Задаём имя mp3 фаулу."""

    return f"temp_{message.chat.username}.mp3"


def create_gen(message: types.Message, page: int = 0):
    """Создаем генератор и записываем его в словарь {имя_пользователя/генератор}"""
    try:
        GENERATORS.set_worker(
            name=message.chat.username,
            # speaker_name='gTTS',
            page=page,
        )
        return speak_text(message)
    except ValueError as e:
        bot.send_message(
            message.chat.id, "Возникла внутренняя ошибка, вас выернут в меню."
        )
        print(e)
    except Exception as e:
        bot.send_message(message.chat.id, "Страницы не существует, вас выернут в меню.")
        print(e)
    return menu(message)


def speak_text(message: types.Message, page: int = 0):
    """Озвучиваем текст."""

    reader: PDFSpeaker = GENERATORS.get_reader(message.chat.username)
    gen: Generator = GENERATORS.get_generator(message.chat.username)
    try:
        text = next(gen)
    except StopIteration:
        bot.reply_to(message, "Книга закончилась")
        log.info(
            "Обработка конца книги.", extra={message.chat.id: message.chat.username}
        )
        return menu(message)
    reader.save_to_file(
        text,
    )
    send_audio(message, reader.file_name_mp3)
    bot.send_message(
        message.chat.id,
        "Страницы с картинками не будут озвучены. Жми далее или в меню.",
        reply_markup=get_speak_text_button(),
    )
    bot.register_next_step_handler(message, read_it)


def read_it(message: types.Message):
    """Обработка выбора сделанного на стартовое сообщение."""

    if message.text == "Следующая страница":
        speak_text(message)
    elif message.text.lower() == "домой":
        menu(message)


def get_speak_text_button() -> types.ReplyKeyboardMarkup:
    """Кнопки после отправки озвученного файла."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(button_next, button_menu)
    return markup


def send_audio(message: types.Message, audio_file):
    try:
        with open(audio_file, "rb") as f:
            bot.send_audio(message.chat.id, audio=f)
    except Exception as e:
        log.exception("Аудио не ушло.", exc_info=True, extra={"Exception": e})
        bot.send_message(message.chat.id, "Возникли проблемы с отправкой.")
        menu(message)


@bot.message_handler(content_types=["document"])
def handle_document(message: types.Message):
    """Загружаем и сохраняем pdf файл."""

    file: types.File
    try:
        file = bot.get_file(message.document.file_id)
    except Exception as e:
        log.exception(
            "Невозможно получить ссылку на загрузку файла.",
            exc_info=False,
            extra={"Exception": e},
        )
        bot.send_message(message.chat.id, "Возникли проблемы с заггрузкой файла.")
        return menu(message)
    log.info(
        "Грузим файл.",
        extra={
            message.chat.username: message.document.file_name,
            "Размер: ": message.document.file_size,
        },
    )
    downloaded_file: bytes = bot.download_file(file.file_path)

    with open(Path(GENERATORS.temp_path, get_filename(message)), "wb") as f:
        f.write(downloaded_file)

    bot.send_message(message.chat.id, "Файл успешно загружен.")
    start_read(message)


if __name__ == "__main__":
    log.info("Поехали")
    bot.infinity_polling()
    log.info("Приехали.")
