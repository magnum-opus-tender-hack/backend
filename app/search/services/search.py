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
from search.services.spell_check import spell_check_ru as spell_check, lemmatize


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
    re = []
    for word in text:
        re.append(word)
    return re


def apply_qs_search(text: str):
    text = _clean_text(text)
    products = Product.objects.none()
    for word in text:
        products = (
            products
            | Product.objects.filter(name__unaccent__trigram_similar=word)
            | Product.objects.filter(name__unaccent__icontains=word)
        )
    products = products.order_by("-score")
    return products


def apply_all_qs_search(orig_qs, text: str):
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
                    if ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i - 1]
                    ).exists():
                        unit = ProductUnitCharacteristic.objects.filter(
                            characteristic__name__icontains=text[i - 1]
                        )
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i]
                        del text[i - 1]
                        break
                elif len(text) - 1 > i >= 1:
                    if ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i - 1]
                    ).exists():
                        unit = ProductUnitCharacteristic.objects.filter(
                            characteristic__name__icontains=text[i - 1]
                        )[0]
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i]
                        del text[i - 1]
                        break
                    elif ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i + 1]
                    ).exists():
                        unit = UnitCharacteristic.objects.filter(
                            ProductUnitCharacteristic=text[i + 1]
                        )[0]
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i]
                        del text[i + 1]
                        break
                else:
                    if ProductUnitCharacteristic.objects.filter(
                        characteristic__name__icontains=text[i + 1]
                    ).exists():
                        unit = ProductUnitCharacteristic.objects.filter(
                            characteristic__name__icontains=text[i + 1]
                        )[0]
                        u_qs = u_qs & process_unit_operation(unit, f"={text[i]}")
                        del text[i]
                        del text[i + 1]
                        break

    prod = Product.objects.filter()
    for word in text:
        car = ProductCharacteristic.objects.filter(
            characteristic__value__icontains=word,
        )
        qs = (
            Product.objects.filter(name__icontains=word)
            | Product.objects.filter(name__unaccent__trigram_similar=word)
            | Product.objects.filter(category__name__icontains=word)
            | Product.objects.filter(characteristics__in=car)
        )
        prod = prod & qs
        if u_qs:
            prod = prod & Product.objects.filter(unit_characteristics__in=u_qs)

    return prod


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
            qs = qs & apply_qs_search(val)
            qs = qs.order_by("-score")
        elif typ == "All":
            qs = apply_all_qs_search(qs, val) & qs
        elif typ == "Category":
            qs = qs.filter(category__name__icontains=val)
            qs = qs.order_by("-score")
        elif typ == "Characteristic":
            char = ProductCharacteristic.objects.filter(product__in=qs)
            char = char.filter(characteristic__value__icontains=val) | char.filter(
                characteristic__value__unaccent__trigram_similar=val
            )
            qs = qs.filter(characteristics__in=char)
            qs = qs.order_by("-score")
        elif typ == "Unknown":
            continue
        else:
            if typ.startswith("*"):
                qs = qs.filter(unit_characteristics__in=val)
            else:
                qs = qs.filter(characteristics__in=val)
    return [x.serialize_self() for x in qs.distinct()[offset : offset + limit]]
