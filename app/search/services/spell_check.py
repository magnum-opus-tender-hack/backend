import pymorphy2
from spellchecker import SpellChecker

speller_ru = SpellChecker(language="ru")
speller_eng = SpellChecker(language="en")


def spell_check_ru(word: str) -> str:
    res = speller_ru.correction(word)
    if not res or not len(res):
        return word
    return res


def spell_check_en(word: str) -> str:
    res = speller_eng.correction(word)
    if not res or not len(res):
        return word
    return res


morph = pymorphy2.MorphAnalyzer()


def lemmatize(word):
    return morph.parse(word)[0].normal_form


def pos(word):
    return morph.parse(word)[0].tag.POS
