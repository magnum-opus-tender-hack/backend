from search.models import Product, Category, Characteristic


def autocomplete_schema(val: str):
    schema = [
        {
            "coordinate": product["name"].lower().index(val.lower()),
            "value": {
                "type": "Name",
                "value": product["name"],
            },
        }
        for product in Product.objects.filter(name__unaccent__icontains=val).values(
            "name"
        )
    ]
    schema.extend(
        [
            {
                "coordinate": cat["name"].lower().index(val.lower()),
                "value": {"type": "Category", "value": cat["name"]},
            }
            for cat in Category.objects.filter(name__unaccent__icontains=val).values(
                "name"
            )
        ]
    )
    schema.extend(
        [
            {
                "coordinate": char["value"].lower().index(val.lower()),
                "value": {"type": char["name"], "value": char["value"]},
            }
            for char in Characteristic.objects.filter(
                value__unaccent__icontains=val
            ).values("name", "value")
        ]
    )
    return schema
