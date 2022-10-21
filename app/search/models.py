from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField("Имя", unique=True, blank=False, max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Category"


class Product(models.Model):
    id = models.IntegerField(
        "ID CTE", primary_key=True, unique=True, blank=False, null=False, db_index=True
    )
    name = models.CharField("Название CTE", unique=True, blank=False, max_length=250)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    characteristic = models.JSONField("Характеристики")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Product"
