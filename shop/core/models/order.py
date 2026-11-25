from django.db import models


class Order(models.Model):
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="orders"
    )
    address = models.ForeignKey("core.Address", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk}"
