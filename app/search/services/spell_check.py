import requests as r


def spell_check(word: str) -> str:
    res = r.get(f'https://speller.yandex.net/services/spellservice.json/checkText?text={word}')
    return res.json()[0]['s'][0]
