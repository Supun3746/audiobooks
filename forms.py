from aiogram.fsm.state import State, StatesGroup


class GetBook(StatesGroup):
    waiting_for_book_name = State()


class AddBook(StatesGroup):
    name = State()
    author = State()
    book = State()
    confirm = State()
