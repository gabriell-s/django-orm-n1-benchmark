from rest_framework import viewsets

from shop.core.models import Product
from shop.core.related import apply_related_modes
from shop.core.related.product import (
    prefetch as product_prefetch,
    select as product_select,
)
from shop.core.serializers.product import ProductSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.order_by("id")
    serializer_class = ProductSerializer

    def get_queryset(self):
        return apply_related_modes(
            super().get_queryset(),
            self.request.query_params,
            select=product_select,
            prefetch=product_prefetch,
        )
