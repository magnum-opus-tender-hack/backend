import requests as r
from conf.settings.base import YANDEX_DICT_API_KEY
from itertools import chain
from typing import List


def translate_ru_en(word: str) -> List[str]:
    res = r.get(
        f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={YANDEX_DICT_API_KEY}&lang=ru-en&text={word}"
    )
    return [i["text"] for i in chain(*[j["tr"] for j in res.json()["def"]])]


def translate_en_ru(word: str) -> List[str]:
    res = r.get(
        f"https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={YANDEX_DICT_API_KEY}&lang=en-ru&text={word}"
    )
    return [i["text"] for i in chain(*[j["tr"] for j in res.json()["def"]])]
