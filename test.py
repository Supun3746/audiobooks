import re
from spellchecker import SpellChecker
from pyaspeller import YandexSpeller


def correct_text(input_text: str) -> str:
    # Инициализация SpellChecker для русского языка
    spell = SpellChecker(language="ru")  # Для русского языка

    # Разделяем текст на слова
    words = input_text.split()

    # Исправляем опечатки в каждом слове
    corrected_words = []
    for word in words:
        # Получаем кандидатов на исправление
        candidates = spell.candidates(word)
        print(candidates)
        # Выбираем первое слово из кандидатов, если оно есть, иначе оставляем оригинальное слово
        corrected_word = next(iter(candidates), word)
        corrected_words.append(corrected_word)

    # Объединяем исправленные слова в текст
    corrected_text = " ".join(corrected_words)

    # Удаление лишних пробелов
    corrected_text = re.sub(
        r"\s+", " ", corrected_text
    )  # Убираем двойные и более пробелы
    corrected_text = corrected_text.strip()  # Убираем пробелы в начале и конце строки

    # Добавляем пробелы после знаков препинания
    corrected_text = re.sub(
        r"([.,!?;:])([^\s])", r"\1 \2", corrected_text
    )  # Пробелы после знаков препинания

    # Убираем повторяющиеся слова (дубли)
    corrected_text = re.sub(r"\b(\w+)( \1\b)+", r"\1", corrected_text)

    # Исправляем регистр: делаем первую букву предложения заглавной
    corrected_text = corrected_text.capitalize()

    return corrected_text


def correct_text2(text: str) -> str:
    spell = YandexSpeller()
    text = text.lower()
    text = re.sub(r"\s+", " ", text)  # Убираем двойные и более пробелы
    text = text.strip()
    text = re.sub(r"([.,!?;:])", r"", text)  # Пробелы после знаков препинания
    changes = {change["word"]: change["s"][0] for change in spell.spell(text)}
    for word, suggestion in changes.items():
        text = text.replace(word, suggestion)
    return text


print(correct_text2("сверхкорость"))
