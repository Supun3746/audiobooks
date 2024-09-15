import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, FSInputFile

from config import settings
from forms import GetBook, AddBook
from utils import create_book, correct_text, get_book


bot = Bot(settings.TOKEN.get_secret_value())
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Введите название книги!")
    await state.set_state(GetBook.waiting_for_book_name)


@dp.message(GetBook.waiting_for_book_name, F.text)
async def get_message(message: Message, state: FSMContext):
    # Здесь выполняется обработка текста и отправка аудиофайла
    corrected_text = correct_text(message.text)
    audio = await get_book(corrected_text)

    if os.path.exists(audio):
        audio_file = FSInputFile(audio)  # Создаем объект для отправки файла

        # Отправляем MP3-файл
        await bot.send_audio(chat_id=message.chat.id, audio=audio_file)
    else:
        await message.answer("Файл не найден!")

    # Сбрасываем состояние после отправки аудиофайла
    await state.clear()


# Обработка команды /add_book
@dp.message(Command("add_book"))
async def add_book(message: Message, state: FSMContext):
    await message.answer("Напишите название книги")
    await state.set_state(AddBook.name)


# Обработка ввода названия книги
@dp.message(AddBook.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Напишите автора книги")
    await state.set_state(AddBook.author)


# Обработка ввода автора
@dp.message(AddBook.author)
async def process_author(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.answer("Загрузите файл аудиокниги")
    await state.set_state(AddBook.book)


# Функция для получения и сохранения аудиофайла
@dp.message(AddBook.book, F.audio)
async def process_book(message: Message, state: FSMContext):
    # Получаем file_id из сообщения
    file_id = message.audio.file_id

    # Получаем объект файла
    file = await bot.get_file(file_id)

    # Путь для сохранения файла
    file_path = os.path.join(
        settings.PATH_TO_BOOKS, f"{message.audio.file_unique_id}.mp3"
    )

    # Загружаем файл
    await bot.download_file(file.file_path, file_path)

    # Сохраняем данные о книге в состоянии
    await state.update_data(book=file_path)

    # Переходим к следующему шагу
    book_data = await state.get_data()
    name = book_data["name"]
    author = book_data["author"]

    await message.answer(f"{name} - {author}. Все верно? (да/нет)")
    await state.set_state(AddBook.confirm)


# Подтверждение сохранения книги
@dp.message(AddBook.confirm)
async def process_confirm(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        await message.answer("Отлично! Данные сохранены.")

        # Получаем данные из состояния
        book_data = await state.get_data()
        name = book_data.get("name")
        author = book_data.get("author")
        book_path = book_data.get("book")  # Путь к загруженному файлу

        # Создаем книгу (функция create_book предполагается, что она сохраняет книгу в базу данных)
        await create_book(name=name, author=author, book=book_path)

        await message.answer(
            f"Книга '{name}' автором '{author}' была успешно добавлена."
        )

        # Очищаем состояние после успешного добавления
        await state.clear()

    elif message.text.lower() == "нет":
        await message.answer("Давай начнем сначала. Напишите название книги.")
        await state.set_state(
            AddBook.name
        )  # Возвращаемся к состоянию ввода названия книги

    else:
        await message.answer("Пожалуйста, ответь 'да' или 'нет'.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
