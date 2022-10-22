from typing import List, Dict

from search.models import Product, Category, Characteristic, UnitCharacteristic


def autocomplete_schema(val: str, exclude: List[Dict]):
    exclude = [dict(x) for x in exclude]
    name_exclude = [x["value"] for x in exclude if x["type"] == "Name"]
    category_exclude = [x["value"] for x in exclude if x["type"] == "Category"]
    schema = []
    if not name_exclude:
        schema.extend(
            [
                {
                    "coordinate": product["name"].lower().index(val.lower()),
                    "value": {
                        "type": "Name",
                        "value": product["name"],
                    },
                }
                for product in Product.objects.filter(name__unaccent__icontains=val)[
                    :20
                ].values("name")
            ]
        )
    if not category_exclude:
        schema.extend(
            [
                {
                    "coordinate": cat["name"].lower().index(val.lower()),
                    "value": {"type": "Category", "value": cat["name"]},
                }
                for cat in Category.objects.filter(name__unaccent__icontains=val)[
                    :20
                ].values("name")
            ]
        )
    schema.extend(
        [
            {
                "coordinate": char["value"].lower().index(val.lower()),
                "value": {"type": char["name"], "value": char["value"]},
            }
            for char in Characteristic.objects.filter(value__unaccent__icontains=val)[
                :20
            ].values("name", "value")
        ]
    )
    schema.extend(
        [
            {
                "coordinate": char["value"].lower().index(val.lower()),
                "value": {
                    "type": char["name"] + "_numeric",
                    "value": char["value"]
                }
            } for char in UnitCharacteristic.objects.filter(value__unaccent__icontains=val)[:20].values("name", "value")
        ]
    )
    return schema
