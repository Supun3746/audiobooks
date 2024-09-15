import re
from pyaspeller import YandexSpeller
from sqlalchemy import select
from config import session_factory, Book


def correct_text(text: str) -> str:
    spell = YandexSpeller()
    text = text.lower()
    text = re.sub(r"\s+", " ", text)  # Убираем двойные и более пробелы
    text = text.strip()
    text = re.sub(r"([.,!?;:])", r"", text)  # Пробелы после знаков препинания
    changes = {change["word"]: change["s"][0] for change in spell.spell(text)}
    for word, suggestion in changes.items():
        text = text.replace(word, suggestion)
    return text


async def create_book(name, author, book):
    async with session_factory() as sess:
        stmt = Book(
            name=correct_text(name),
            author=correct_text(author),
            book=book,
        )
        sess.add(stmt)
        await sess.commit()
    return {"create book": "OK"}


async def get_book(name):
    async with session_factory() as sess:
        stmt = select(Book.book).where(Book.name == name)
        res = await sess.execute(stmt)
        res = res.scalar()
    return res
