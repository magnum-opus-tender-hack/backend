# Generated by Django 4.1.2 on 2022-10-21 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=250, unique=True, verbose_name="Имя"),
                ),
            ],
            options={
                "db_table": "Category",
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        db_index=True,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name="ID CTE",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=250, unique=True, verbose_name="Название CTE"
                    ),
                ),
                ("characteristic", models.JSONField(verbose_name="Характеристики")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="search.category",
                    ),
                ),
            ],
            options={
                "db_table": "Product",
            },
        ),
    ]
