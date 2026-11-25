from django.db import models


class Review(models.Model):
    product = models.ForeignKey(
        "core.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField()

    def __str__(self):
        return f"{self.product} - {self.rating}"
