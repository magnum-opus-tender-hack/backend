from search.models import Product
from typing import List


def process_string(text: str) -> List[dict]:
    return [x.serialize_self() for x in Product.objects.filter(name__contains=text)[5:]]
