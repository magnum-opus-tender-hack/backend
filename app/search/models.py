from django.db import models


class Category(models.Model):
    name = models.CharField("Имя", unique=True, blank=False, max_length=250)
    value = models.CharField("Имя", unique=True, blank=False, max_length=250)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "Category"


class Product(models.Model):
    id = models.IntegerField(
        "ID CTE", primary_key=True, unique=True, blank=False, null=False, db_index=True
    )
    name = models.CharField("Название CTE", unique=True, blank=False, max_length=250)
    characteristic = models.JSONField("Характеристики")

    def __str__(self):
        return str(self.name)

    def serialize_self(self) -> dict:
        return {
            'name': self.name,
            'characteristic': self.characteristic,
        }

    class Meta:
        db_table = "Product"


class ProductInCategory(models.Model):
    product = models.ForeignKey(
        Product, related_name="categories", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.product} in {self.category}"
