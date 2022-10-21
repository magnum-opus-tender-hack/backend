from search.models import Product


def process_string(text: str) -> [dict]:
    return [x.serialize_self() for x in Product.objects.filter(name__contains=text)[5:]]
