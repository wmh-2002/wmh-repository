from rest_framework import serializers
from .models import Category, Product, ProductImage, Address


class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'icon', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    """照片序列化器"""

    class Meta:
        model = ProductImage
        fields = ['image_url', 'uploaded_at']


class AddressSerializer(serializers.ModelSerializer):
    """地址序列化器"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ['id', 'name', 'level', 'parent', 'children']

    def get_children(self, obj):
        return AddressSerializer(obj.children.all(), many=True).data


class CategoryOneSerializer(serializers.ModelSerializer):
    """序列name"""

    class Meta:
        model = Category
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    contact_number = serializers.SerializerMethodField()  # 动态获取字段

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'user', 'price', 'stock', 'category', 'created_at', 'updated_at',
                  "status", "shopping_address", "images", "contact_number", 'sale_status', 'under_price']

    def get_contact_number(self, obj):
        """
        获取实例用户的手机号
        :param obj:产品示例
        :return:
        """
        # 检查 user 是否存在，并返回其 mobile 字段
        return obj.user.mobile if obj.user and hasattr(obj.user, 'mobile') else None


class AddProductSerializer(serializers.ModelSerializer):
    """上架商品序列化器"""

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'user', 'price', 'stock', 'category', 'created_at', 'updated_at',
                  "status", "shopping_address", ]
