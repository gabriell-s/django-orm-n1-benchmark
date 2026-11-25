from rest_framework import viewsets

from shop.core.models import User
from shop.core.related import apply_related_modes
from shop.core.related.user import prefetch as user_prefetch
from shop.core.serializers.user import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.order_by("id")
    serializer_class = UserSerializer

    def get_queryset(self):
        return apply_related_modes(
            super().get_queryset(),
            self.request.query_params,
            prefetch=user_prefetch,
        )
