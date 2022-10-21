from ast import literal_eval

import pandas as pd

from search.models import Product, Category


def load():
    with open("data.json", "r", encoding="utf-16") as f:
        data = literal_eval(f.read())

    for el in data:
        Product.objects.get_or_create(id=el)
        print(el["characteristic"])


def load_excel():
    df = pd.read_excel("data1.xlsx", sheet_name="Sheet1")
    for row in range(df.shape[0]):
        product = Product.objects.get_or_create(id=df.iat[row, 0])
        product.name = df.iat[row, 1]
        product.name = Category.objects.get_or_create(name=df.iat[row, 2])
        for cat in df.iat[row, 4]:
            pass

