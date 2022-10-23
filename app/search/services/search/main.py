from typing import List

from search.services.search.methods import (
    apply_qs_search,
    apply_all_qs_search,
    apply_qs_category,
    appy_qs_characteristic,
)
from search.services.search.prepare import apply_union
from search.models import Product


def process_search(data: List[dict], limit=5, offset=0) -> List[dict]:
    prep_data = apply_union(data)
    # ----------------------------------- apply filters on QuerySet -------------------------------------------------- #
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
    return [x.serialize_self() for x in qs.distinct()[offset : offset + limit]]
