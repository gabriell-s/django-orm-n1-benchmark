from rest_framework import viewsets

from shop.core.models import Order
from shop.core.related import apply_related_modes
from shop.core.related.order import prefetch as order_prefetch, select as order_select
from shop.core.serializers.order import OrderSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.order_by("id")
    serializer_class = OrderSerializer

    def get_queryset(self):
        return apply_related_modes(
            super().get_queryset(),
            self.request.query_params,
            select=order_select,
            prefetch=order_prefetch,
        )
