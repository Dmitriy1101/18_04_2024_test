from typing import Generator
import telebot
import os
from pathlib import Path
from dotenv import load_dotenv
from telebot import types
from core.bot_settings import GENERATORS, get_logger
from core.bot_speaker import PDFSpeaker

load_dotenv()

# Инициализация Telegram бота
TOKEN: str = os.environ.get("speaker_bot")
bot = telebot.TeleBot(TOKEN)

log = get_logger(__name__) 

next_markup = telebot.types.InlineKeyboardMarkup()
button_next = telebot.types.InlineKeyboardButton(
    text="Следующая страница", callback_data="next_page"
)
button_menu = telebot.types.InlineKeyboardButton(text="Меню", callback_data="menu")
next_markup.add(button_next, button_menu)


@bot.callback_query_handler(func=lambda call: True)
def call_main(call: types.CallbackQuery):
    """Основной обработчик функций обратного вызова."""

    if call.data.lower() == "next_page":
        speak_text(call.message)
    elif call.data.lower() == "menu":
        menu(call.message)


def get_filename(message: types.Message) -> str:
    """Задаём имя загруженному фаулу."""

    return f"temp_{message.chat.username}.pdf"


def get_file(file_name: str) -> bool:
    """Ищем сохраненный файл."""

    return os.path.isfile(Path(GENERATORS.temp_path, file_name))


@bot.message_handler(commands=["start"])
def send_welcome(message: types.Message):
    """Обработчик команды start"""

    log.info("Приперся тут один.", extra={message.chat.id: message.chat.username})
    bot.send_message(message.chat.id, "Привет! Я озвучиваю PDF книги")
    menu(message)


def menu(message: types.Message):
    """Главное меню бота."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buts: list[types.KeyboardButton] = []
    buts.append(types.KeyboardButton("Загрузить PDF файл"))

    if get_file(get_filename(message)):
        buts.append(types.KeyboardButton("Использовать загруженый файл"))
    bot.send_message(
        message.chat.id,
        "Отправь мне прикреплённый PDF файл, я могу озвучить его текст. \
            \nЕсли я найду старый файл мы можем прослушать его.",
        reply_markup=markup.row(*buts),
    )
    bot.register_next_step_handler(message, got_it)


def got_it(message: types.Message):
    """Обработка выбора сделанного на стартовое сообщение."""

    if message.text == "Загрузить PDF файл":
        bot.send_message(message.chat.id, "Отправьте PDF файл.")
    elif message.text == "Использовать загруженый файл":
        bot.send_message(message.chat.id, "Принято.")
        start_read(message)


def start_read(message: types.Message):
    """Спрашиваем про страницу."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(types.KeyboardButton("С начала"), types.KeyboardButton("Домой"))
    bot.send_message(
        message.chat.id,
        "Читаем с начала? Или введи номер страницы.",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, get_psge)


def get_mp3_filename(message: types.Message) -> str:
    """Задаём имя mp3 фаулу."""

    return f"temp_{message.chat.username}.mp3"


def get_psge(message: types.Message):
    """Узнаём страницу с которой читаемю"""

    if message.text == "С начала":
        create_gen(message)
    elif message.text == "Домой":
        menu(message)
    elif message.text.isdigit():
        create_gen(message, page=int(message.text))
    else:
        start_read(message)


def create_gen(message: types.Message, page: int = 0):
    """Создаем генератор и записываем его в словарь {имя_пользователя/генератор}"""
    try:
        GENERATORS.set_genegator(
            name=message.chat.username,
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
        reply_markup=next_markup,
    )


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
