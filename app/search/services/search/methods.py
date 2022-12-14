from typing import List

from search.models import (
    Product,
    ProductCharacteristic,
    ProductUnitCharacteristic,
)
from search.services.spell_check import pos, spell_check


def _clean_text(text: str) -> List[str]:

    for st in [".", ",", "!", "?"]:
        text = text.replace(st, " ")

    text = text.split()
    functors_pos = {"INTJ", "PRCL", "CONJ", "PREP"}  # function words

    text = [word for word in text if pos(word) not in functors_pos]

    text = [spell_check(x) for x in text]

    return text


def process_unit_operation(unit: ProductUnitCharacteristic.objects, operation: str):
    if operation.startswith("<=") or operation.startswith("=<"):
        return unit.filter(
            characteristic__numeric_value_max__lte=int(float(operation[2:]))
        )
    elif operation.startswith("=>") or operation.startswith(">="):
        return unit.filter(
            characteristic__numeric_value_min__gte=int(float(operation[2:]))
        )
    elif operation.startswith(">"):
        return unit.filter(
            characteristic__numeric_value_min__gt=int(float(operation[1:]))
        )
    elif operation.startswith("<"):
        return unit.filter(
            characteristic__numeric_value_max__lt=int(float(operation[1:]))
        )
    elif operation.startswith("="):
        return unit.filter(
            characteristic__numeric_value_min__gte=int(float(operation[1:])),
            characteristic__numeric_value_max__lte=int(float(operation[1:])),
        )
    return unit


def apply_qs_search(text: str):
    text = _clean_text(text)
    qs = Product.objects.filter()
    for word in text:
        qs = qs.filter(name__unaccent__trigram_similar=word) | qs.filter(
            name__unaccent__icontains=word
        )
    products = qs.order_by("-score")
    return products


def apply_all_qs_search(text: str):
    # words
    text = _clean_text(text)

    u_qs = None

    # try to find Unit characteristics
    if any(x.isnumeric() for x in text):
        u_qs = ProductUnitCharacteristic.objects.filter()
        for i in range(len(text)):
            el = text[i]
            if el.isnumeric():
                if i == len(text) - 1:
                    if unit := ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i - 1]
                    ):
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i - 1]
                        del text[i - 1]
                        break
                elif len(text) - 1 > i >= 1:
                    if unit := ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i + 1]
                    ):
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i]
                        del text[i]
                        break
                    elif unit := ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i - 1]
                    ):
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i - 1]
                        del text[i - 1]
                        break
                else:
                    if unit := ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i + 1]
                    ):
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i]
                        del text[i]
                        break

    if u_qs:
        prod = Product.objects.filter(unit_characteristics__in=u_qs)
    else:
        prod = Product.objects.filter()

    for word in text:
        car = ProductCharacteristic.objects.filter(
            characteristic__value__icontains=word,
        ) | ProductCharacteristic.objects.filter(
            characteristic__value__trigram_similar=word,
        )
        qs = (
            Product.objects.filter(name__icontains=word)
            | Product.objects.filter(characteristics__in=car)
            | Product.objects.filter(category__name__icontains=word)
            | Product.objects.filter(name__trigram_similar=word)
        )
        if any(
            x in word
            for x in "????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????"
        ):
            qs = qs | Product.objects.filter(
                name__icontains=word.translate(
                    str.maketrans(
                        "????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????",
                        "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA",
                    )
                )
            )
        prod = prod & qs

    return prod


def apply_qs_category(qs, name: str):
    qs = qs.filter(category__name__icontains=name)
    return qs


def appy_qs_characteristic(qs, name: str):
    char = ProductCharacteristic.objects.filter(product__in=qs)
    char = char.filter(characteristic__value__icontains=name) | char.filter(
        characteristic__value__unaccent__trigram_similar=name
    )
    qs = qs.filter(characteristics__in=char)
    return qs
