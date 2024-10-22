from rest_framework import serializers
from .models import CartItem
from SecondHandBackend.apps.product.serializer import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """购物车序列化器"""
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'added_at']
