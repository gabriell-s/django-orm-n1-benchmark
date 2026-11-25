from django.db import models


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        "core.Order",
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.status}"
