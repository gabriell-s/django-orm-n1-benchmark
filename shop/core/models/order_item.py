from django.db import models


class OrderItem(models.Model):
    order = models.ForeignKey(
        "core.Order", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey("core.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product}"
