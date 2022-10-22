from search.models import Product, Category, Characteristic


def autocomplete_schema(val: str):
    schema = []
    schema.extend(
        [
            {
                "coordinate": product["name"].index(val),
                "value": {
                    "type": "Name",
                    "value": product["name"],
                },
            }
            for product in Product.objects.filter(name__contains=val).values("name")
        ]
    )
    schema.extend(
        [
            {
                "coordinate": cat["name"].index(val),
                "value": {"type": "Category", "value": cat["name"]},
            }
            for cat in Category.objects.filter(name__contains=val).values("name")
        ]
    )
    schema.extend(
        [
            {
                "coordinate": char["name"].index(val),
                "value": {"type": char["name"], "value": char["value"]},
            }
            for char in Characteristic.objects.filter(name__contains=val).values(
                "name", "value"
            )
        ]
    )
    return schema
