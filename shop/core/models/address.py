from django.db import models


class Address(models.Model):
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="addresses"
    )
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}"
