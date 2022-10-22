import string

from django.db.models import QuerySet

from search.models import (
    Product,
    Characteristic,
    ProductCharacteristic,
    ProductUnitCharacteristic,
    UnitCharacteristic,
    Category,
)
from typing import List

from search.services.hints import get_hints
from search.services.spell_check import spell_check
from search.services.translate import translate_en_ru, translate_ru_en


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


def _clean_text(text: str) -> List[str]:
    for st in [".", ",", "!", "?"]:
        text = text.replace(st, " ")
    text = text.split()
    return text


def apply_qs_search(qs: Product.objects, text: str):
    text = _clean_text(text)
    words = Product.objects.none()
    for word in text:
        words = (
            words
            | Product.objects.filter(name__unaccent__trigram_similar=word)
            | Product.objects.filter(name__unaccent__icontains=word)
        )
    print(words)
    qs = qs | words
    print(qs)
    return qs


def apply_all_qs_search(orig_qs, text: str):
    # words
    qs = apply_qs_search(Product.objects.none(), text)
    text = _clean_text(text)

    # categories
    cats = Category.objects.none()
    for word in text:
        cats = cats | cats.filter(name__icontains=word)
    qs = qs | Product.objects.filter(category__in=cats)

    # characteristics
    chars = Characteristic.objects.none()
    for word in text:
        chars = chars | chars.filter(
            value__icontains=word,
        )
    qs = qs | Product.objects.filter(characteristics__characteristic__in=chars)
    # print(qs)

    return qs & orig_qs


def process_search(data: List[dict], limit=5, offset=0) -> List[dict]:
    prep_data = []
    prep_dict = {}
    prep_dict_char_type = {}
    # --------------------------------------- prepare filters -------------------------------------------------------- #
    for x in data:
        dat = dict(x)
        if x["type"] in ["Name", "Category", "Characteristic", "All"]:
            prep_data.append(
                {
                    "type": dat["type"],
                    "value": spell_check(
                        dat["value"],
                    ),
                }
            )
        elif x["type"] == "Unknown":
            type = get_hints(dat["value"])
            prep_data.append(
                {
                    "type": type,
                    "value": spell_check(
                        dat["value"],
                    ),
                }
            )
        else:
            val = spell_check(
                dat["value"],
            )
            if x["type"] in list(prep_dict.keys()):
                if x["type"].startswith("*"):
                    unit = ProductUnitCharacteristic.objects.filter(
                        characteristic__in=prep_dict_char_type[x["type"]],
                    )
                    prep_dict[x["type"]] = prep_dict[
                        x["type"]
                    ] | process_unit_operation(unit, x["value"])
                else:
                    prep_dict[x["type"]] = (
                        prep_dict[x["type"]]
                        | ProductCharacteristic.objects.filter(
                            characteristic__in=prep_dict_char_type[x["type"]],
                            characteristic__value__unaccent__trigram_similar=val,
                        )
                        | ProductCharacteristic.objects.filter(
                            characteristic__in=prep_dict_char_type[x["type"]],
                            characteristic__value__icontains=val,
                        )
                    )
            else:
                if x["type"].startswith("*"):
                    prep_dict_char_type[x["type"]] = UnitCharacteristic.objects.filter(
                        name__unaccent__trigram_similar=x["type"]
                    ) | UnitCharacteristic.objects.filter(name__icontains=x["type"])
                    unit = ProductUnitCharacteristic.objects.filter(
                        characteristic__in=prep_dict_char_type[x["type"]],
                    )
                    prep_dict[x["type"]] = process_unit_operation(unit, x["value"])
                else:
                    prep_dict_char_type[x["type"]] = Characteristic.objects.filter(
                        name__unaccent__trigram_similar=x["type"]
                    ) | Characteristic.objects.filter(name__icontains=x["type"])
                    prep_dict[x["type"]] = ProductCharacteristic.objects.filter(
                        characteristic__in=prep_dict_char_type[x["type"]],
                        characteristic__value__unaccent__trigram_similar=val,
                    ) | ProductCharacteristic.objects.filter(
                        characteristic__in=prep_dict_char_type[x["type"]],
                        characteristic__value__icontains=val,
                    )
    for el, val in prep_dict.items():
        prep_data.append({"type": el, "value": val})
    # ----------------------------------- apply filters on QuerySet -------------------------------------------------- #
    qs = Product.objects.filter()
    for x in prep_data:
        typ = x["type"]
        val = x["value"]
        if typ == "Name":
            qs = apply_qs_search(qs, val)
        elif typ == "All":
            qs = apply_all_qs_search(qs, val)
        elif typ == "Category":
            qs = qs.filter(category__name__unaccent__trigram_similar=val) | qs.filter(
                category__name__icontains=val
            )
        elif typ == "Characteristic":
            char = ProductCharacteristic.objects.filter(product__in=qs)
            char = char.filter(characteristic__value__icontains=val) | char.filter(
                characteristic__value__unaccent__trigram_similar=val
            )
            qs = qs.filter(characteristics__in=char)
        elif typ == "Unknown":
            if val[0] in string.printable:
                val = "".join(translate_en_ru(val))
            else:
                val = "".join(translate_ru_en(val))
            type = get_hints(val)
            if type == "Name":
                qs = apply_qs_search(qs, val)
            elif type == "Category":
                qs = qs.filter(category__name__unaccent__trigram_similar=val)
            elif type == "Unknown":
                continue
            else:
                qs = qs.filter(
                    characteristics__characteristic__name__unaccent__trigram_similar=val
                )
            continue
        else:
            if typ.startswith("*"):
                qs = qs.filter(unit_characteristics__in=val)
            else:
                qs = qs.filter(characteristics__in=val)
    return [
        x.serialize_self()
        for x in qs.distinct().order_by("-score")[offset : offset + limit]
    ]
