from django.db import models


class Stock(models.Model):
    product = models.OneToOneField(
        "core.Product",
        on_delete=models.CASCADE,
        related_name="stock",
    )
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product} ({self.quantity})"
