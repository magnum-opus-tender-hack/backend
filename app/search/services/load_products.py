from ast import literal_eval

import pandas as pd

from search.models import (
    Product,
    Category,
    UnitCharacteristic,
    ProductUnitCharacteristic,
    ProductCharacteristic,
    Characteristic,
)


def load():
    with open("data.json", "r", encoding="utf-16") as f:
        data = literal_eval(f.read())

    for el in data:
        Product.objects.get_or_create(id=el)
        print(el["characteristic"])


def load_excel():
    df = pd.read_excel("data.xlsx", sheet_name="Запрос1")
    for row in range(df.shape[0]):
        try:
            print(df.iat[row, 0], df.iat[row, 1], df.iat[row, 2])
            if Product.objects.filter(id=df.iat[row, 0]).exists():
                Product.objects.filter(id=df.iat[row, 0]).delete()
            product = Product(id=df.iat[row, 0])
            product.name = df.iat[row, 1]
            category = Category.objects.get_or_create(name=df.iat[row, 2])[0]
            product.category = category
            product.save()
            if df.iat[row, 4]:
                for cat in literal_eval(df.iat[row, 4]):
                    try:
                        if "Unit" in cat:
                            ProductUnitCharacteristic.objects.get_or_create(
                                characteristic=UnitCharacteristic.objects.get_or_create(
                                    name=cat["Name"],
                                    value=cat["Value"],
                                    unit=cat["Unit"],
                                )[0],
                                product=product,
                            )
                        else:
                            ProductCharacteristic.objects.get_or_create(
                                characteristic=Characteristic.objects.get_or_create(
                                    name=cat["Name"], value=cat["Value"]
                                )[0],
                                product=product,
                            )
                    except KeyError:
                        # Empty Value
                        continue
        except BaseException:
            # malformed node or string: nan \ duplicate key
            print("СКОРОСШИВАТЕЛЬ")
            continue
