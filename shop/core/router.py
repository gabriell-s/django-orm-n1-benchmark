from rest_framework import routers

from shop.core.views.order import OrderViewSet
from shop.core.views.product import ProductViewSet
from shop.core.views.user import UserViewSet

router = routers.SimpleRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"products", ProductViewSet, basename="product")
