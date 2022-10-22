from search.models import Product, Characteristic, ProductCharacteristic
from typing import List


def process_search(data: List[dict]) -> List[dict]:
    prep_data = []
    prep_dict = {}
    prep_dict_char_type = {}

    for x in data:
        dat = dict(x)
        if x["type"] in ["Name", "Category", "Unknown"]:
            prep_data.append(dat)
        else:
            if x["type"] in list(prep_dict.keys()):
                prep_dict[x["type"]] = prep_dict[
                    x["type"]
                ] | ProductCharacteristic.objects.filter(
                    characteristic__in=prep_dict_char_type[x["type"]],
                    characteristic__value__unaccent__trigram_similar=x["value"],
                )
            else:
                prep_dict_char_type[x["type"]] = Characteristic.objects.filter(
                    name__contains=x["type"]
                )
                prep_dict[x["type"]] = ProductCharacteristic.objects.filter(
                    characteristic__in=prep_dict_char_type[x["type"]],
                    characteristic__value__unaccent__trigram_similar=x["value"],
                )
    for el, val in prep_dict.items():
        prep_data.append({"type": el, "value": val})
    qs = Product.objects.filter()
    for x in prep_data:
        typ = x["type"]
        val = x["value"]
        if typ == "Name":
            qs = qs.filter(name__unaccent__trigram_similar=val)
        elif typ == "Category":
            qs = qs.filter(category__name__unaccent__trigram_similar=val)
        elif typ == "Unknown":
            continue
        else:
            qs = qs.filter(characteristics__in=val)
    return [x.serialize_self() for x in qs[:5]]
