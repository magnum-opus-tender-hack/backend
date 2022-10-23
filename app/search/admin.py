from django.contrib import admin

from search.models import (
    Characteristic,
    UnitCharacteristic,
    Category,
    Product,
    ProductCharacteristic,
    ProductUnitCharacteristic,
)

# Register your models here.


admin.site.register(Characteristic)
admin.site.register(UnitCharacteristic)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductCharacteristic)
admin.site.register(ProductUnitCharacteristic)
