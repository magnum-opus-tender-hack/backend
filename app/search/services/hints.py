from search.models import Product, Category, Characteristic


def get_hints(content: str) -> str:
    category = "Unknown"
    if content in list(map(lambda product: product.name, Product.objects.all())):
        category = "Name"
    elif content in list(map(lambda category: category.name, Category.objects.all())):
        category = "Category"
    elif content in list(map(lambda char: char.value, Characteristic.objects.all())):
        category = Characteristic.objects.filter(value=content).first().name
    return category
