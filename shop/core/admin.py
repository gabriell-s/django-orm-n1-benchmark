from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from shop.core.models import (
    Address,
    Category,
    Order,
    OrderItem,
    OrderStatusHistory,
    Product,
    Review,
    Stock,
    Tag,
    User,
)


admin.site.register(User, UserAdmin)
admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderStatusHistory)
