from django.db import models


class Characteristic(models.Model):
    name = models.TextField("Имя", blank=False)
    value = models.TextField("Значение", blank=False)

    def __str__(self):
        return str(self.name)

    def serialize_self(self):
        return {"name": self.name, "value": self.value}

    class Meta:
        db_table = "characteristic"


class UnitCharacteristic(models.Model):
    name = models.TextField("Имя", blank=False)
    value = models.TextField("Значение", blank=False)
    unit = models.TextField("Размерность", blank=False)

    def __str__(self):
        return str(self.name)

    def serialize_self(self):
        return {"name": self.name, "value": self.value, "unit": self.unit}

    class Meta:
        db_table = "unit_characteristic"


class Category(models.Model):
    name = models.TextField("Имя", unique=True, blank=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "category"


class Product(models.Model):
    id = models.IntegerField(
        "ID CTE", primary_key=True, unique=True, blank=False, null=False, db_index=True
    )
    name = models.TextField("Название CTE", unique=True, blank=False)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.name)

    def serialize_self(self) -> dict:
        return {
            "name": self.name,
            "characteristic": [
                x.serialize_self() for x in self.characteristics.objects.all()
            ]
            + [x.serialize_self() for x in self.unit_characteristics.objects.all()],
        }

    class Meta:
        db_table = "product"


class ProductCharacteristic(models.Model):
    product = models.ForeignKey(
        Product, related_name="characteristics", on_delete=models.CASCADE
    )
    characteristic = models.ForeignKey(
        Characteristic, related_name="products", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.product} in {self.characteristic}"

    class Meta:
        db_table = "product_characteristic"


class ProductUnitCharacteristic(models.Model):
    product = models.ForeignKey(
        Product, related_name="unit_characteristics", on_delete=models.CASCADE
    )
    characteristic = models.ForeignKey(
        UnitCharacteristic, related_name="products", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.product} in {self.characteristic}"

    class Meta:
        db_table = "product_unit_characteristic"
