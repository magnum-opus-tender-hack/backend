from search.models import Product, Category


def get_hints(content: str) -> str:
    category = 'Unknown'
    if content in list(map(lambda product: product.name, Product.objects.all())):
        category = 'Name'
    return category
