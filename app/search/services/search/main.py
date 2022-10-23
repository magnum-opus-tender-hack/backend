from typing import List

from search.services.search.methods import (
    apply_qs_search,
    apply_all_qs_search,
    apply_qs_category,
    appy_qs_characteristic,
)
from search.services.search.prepare import apply_union
from search.models import Product


def call(prep_data):
    if len(prep_data) == 1:
        typ = prep_data[0]["type"]
        val = prep_data[0]["value"]
        if typ == "Name":
            return apply_qs_search(val).order_by("-score")
        elif typ == "All":
            return apply_all_qs_search(val).order_by("-score")
        elif typ == "Category":
            return Product.objects.filter(category__name__icontains=val).order_by(
                "-score"
            )
        elif typ == "Characteristic":
            return appy_qs_characteristic(Product.objects.filter(), val).order_by(
                "-score"
            )
        elif typ == "Unknown":
            return []
        else:
            if typ.startswith("*"):
                return Product.objects.filter(unit_characteristics__in=val)
            else:
                return Product.objects.filter(characteristics__in=val)
    qs = Product.objects.filter()
    for x in prep_data:
        typ = x["type"]
        val = x["value"]
        if typ == "Name":
            qs = qs & apply_qs_search(val)
            qs = qs.order_by("-score")
        elif typ == "All":
            qs = apply_all_qs_search(val) & qs
        elif typ == "Category":
            qs = apply_qs_category(qs, val)
            qs = qs.order_by("-score")
        elif typ == "Characteristic":
            qs = appy_qs_characteristic(qs, val)
            qs = qs.order_by("-score")
        elif typ == "Unknown":
            continue
        else:
            if typ.startswith("*"):
                qs = qs.filter(unit_characteristics__in=val)
            else:
                qs = qs.filter(characteristics__in=val)
    return []


def process_search(body: List[dict], limit=5, offset=0) -> List[dict]:
    prep_data = apply_union(body)
    return call(prep_data)[offset : offset + limit]
