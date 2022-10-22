import requests as r
from spellchecker import SpellChecker

speller = SpellChecker(language='ru')

def spell_check(word: str) -> str:
    res = speller.correction(word)
    if not len(res): 
        return word
    return res
