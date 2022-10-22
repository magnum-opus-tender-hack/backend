import string

from search.models import (
    Product,
    Characteristic,
    ProductCharacteristic,
    ProductUnitCharacteristic,
    UnitCharacteristic,
)
from typing import List

from search.services.hints import get_hints
from search.services.spell_check import spell_check
from search.services.translate import translate_en_ru, translate_ru_en


def process_unit_operation(unit: ProductUnitCharacteristic.objects, operation: str):
    if operation.startswith("<=") or operation.startswith("=<"):
        return unit.filter(characteristic__numeric_value__lte=int(float(operation[2:])))
    elif operation.startswith("=>") or operation.startswith(">="):
        return unit.filter(characteristic__numeric_value__gte=int(float(operation[2:])))
    elif operation.startswith(">"):
        return unit.filter(characteristic__numeric_value__gt=int(float(operation[1:])))
    elif operation.startswith("<"):
        return unit.filter(characteristic__numeric_value__lt=int(float(operation[1:])))
    elif operation.startswith("="):
        return unit.filter(characteristic__numeric_value=int(float(operation[1:])))
    return unit


def process_search(data: List[dict], limit=5, offset=0) -> List[dict]:
    prep_data = []
    prep_dict = {}
    prep_dict_char_type = {}
    # --------------------------------------- prepare filters -------------------------------------------------------- #
    for x in data:
        dat = dict(x)
        if x["type"] in ["Name", "Category"]:
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
                    prep_dict[x["type"]] = prep_dict[
                        x["type"]
                    ] | ProductCharacteristic.objects.filter(
                        characteristic__in=prep_dict_char_type[x["type"]],
                        characteristic__value__unaccent__trigram_similar=val,
                    )
            else:
                if x["type"].startswith("*"):
                    prep_dict_char_type[x["type"]] = UnitCharacteristic.objects.filter(
                        name__unaccent__trigram_similar=x["type"]
                    )
                    unit = ProductUnitCharacteristic.objects.filter(
                        characteristic__in=prep_dict_char_type[x["type"]],
                    )
                    prep_dict[x["type"]] = process_unit_operation(unit, x["value"])
                else:
                    prep_dict_char_type[x["type"]] = Characteristic.objects.filter(
                        name__unaccent__trigram_similar=x["type"]
                    )
                    prep_dict[x["type"]] = ProductCharacteristic.objects.filter(
                        characteristic__in=prep_dict_char_type[x["type"]],
                        characteristic__value__unaccent__trigram_similar=val,
                    )
    for el, val in prep_dict.items():
        prep_data.append({"type": el, "value": val})
    # ----------------------------------- apply filters on QuerySet -------------------------------------------------- #
    qs = Product.objects.filter()
    for x in prep_data:
        typ = x["type"]
        val = x["value"]
        if typ == "Name":
            qs = qs.filter(name__unaccent__trigram_similar=val)
        elif typ == "Category":
            qs = qs.filter(category__name__unaccent__trigram_similar=val)
        elif typ == "Unknown":
            if val[0] in string.printable:
                val = "".join(translate_en_ru(val))
            else:
                val = "".join(translate_ru_en(val))
            type = get_hints(val)
            if type == "Name":
                qs = qs.filter(name__unaccent__trigram_similar=val)
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
    return [x.serialize_self() for x in qs[offset : offset + limit]]
