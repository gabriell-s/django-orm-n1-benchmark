from rest_framework import serializers


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)


class TagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class OrderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product = ProductSerializer(read_only=True)
    quantity = serializers.IntegerField()


class AddressSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    street = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=100)


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    address = AddressSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(max_length=150, allow_blank=True)
    last_name = serializers.CharField(max_length=150, allow_blank=True)
    addresses = AddressSerializer(many=True, read_only=True)
    orders = OrderSerializer(many=True, read_only=True)
