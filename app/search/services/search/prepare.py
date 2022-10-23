from typing import List, Dict

from rest_framework.exceptions import ValidationError

from search.models import Characteristic, ProductCharacteristic, ProductUnitCharacteristic, UnitCharacteristic
from search.services.hints import get_hints
from search.services.search.methods import process_unit_operation
)
from search.services.spell_check import spell_check_ru as spell_check


def apply_union(data: List[Dict]) -> List[Dict]:
    prep_data = []
    prep_dict = {}
    prep_dict_char_type = {}
    # --------------------------------------- prepare filters -------------------------------------------------------- #
    for x in data:
        dat = dict(x)
        if "type" not in dat or "value" not in dat:
            raise ValidationError("Improper body structure")

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
    return prep_data
