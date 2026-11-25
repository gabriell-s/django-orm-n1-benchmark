from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        "core.Category",
        on_delete=models.CASCADE,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tags = models.ManyToManyField("core.Tag", related_name="products")

    def __str__(self):
        return self.name
