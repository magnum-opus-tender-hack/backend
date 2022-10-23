from typing import List, Dict

from search.models import Product, Category, Characteristic, UnitCharacteristic


def autocomplete_schema(val: str, exclude: List[Dict]):
    exclude = [dict(x) for x in exclude]
    name_exclude = [x["value"] for x in exclude if x["type"] == "Name"]
    category_exclude = [x["value"] for x in exclude if x["type"] == "Category"]
    schema = []
    if not category_exclude:
        schema.extend(
            [
                {
                    "coordinate": cat["name"]
                    .replace("ё", "е")
                    .lower()
                    .index(val.lower()),
                    "value": {"type": "Category", "value": cat["name"]},
                }
                for cat in (
                    Category.objects.filter(name__unaccent__istartswith=val)
                    | Category.objects.filter(name__unaccent__icontains=val)
                )
                .distinct()[:10]
                .values("name")
            ]
        )
    if not name_exclude:
        schema.extend(
            [
                {
                    "coordinate": product["name"]
                    .replace("ё", "е")
                    .lower()
                    .index(val.lower()),
                    "value": {
                        "type": "Name",
                        "value": product["name"],
                    },
                }
                for product in (
                    Product.objects.filter(name__unaccent__istartswith=val)
                    | Product.objects.filter(name__unaccent__icontains=val)
                )
                .distinct()[:30]
                .values("name")
            ]
        )
    schema.extend(
        [
            {
                "coordinate": char["value"]
                .replace("ё", "е")
                .lower()
                .index(val.lower()),
                "value": {"type": char["name"], "value": char["value"]},
            }
            for char in (
                Characteristic.objects.filter(value__unaccent__istartswith=val)
                | Characteristic.objects.filter(value__unaccent__icontains=val)
            )
            .distinct()[:20]
            .values("name", "value")
        ]
    )
    schema.extend(
        [
            {
                "coordinate": char["name"].lower().replace("ё", "е").index(val.lower()),
                "value": {"type": char["name"] + "_numeric", "value": char["name"]},
            }
            for char in UnitCharacteristic.objects.filter(
                name__unaccent__icontains=val
            )[:20].values("name", "value")
        ]
    )
    return schema
