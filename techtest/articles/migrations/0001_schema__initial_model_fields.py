# Generated by Django 3.2.7 on 2021-09-12 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("regions", "0001_schema__initial_model_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
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
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField(blank=True)),
                (
                    "regions",
                    models.ManyToManyField(
                        blank=True, related_name="articles", to="regions.Region"
                    ),
                ),
            ],
        ),
    ]
