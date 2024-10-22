import uuid

from django.db import models
from SecondHandBackend.apps.users.models import UserProfile


class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=100, verbose_name="分类名称")
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="父分类"
    )
    icon = models.CharField(max_length=64, verbose_name="图标", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Address(models.Model):
    """地址表"""
    LEVEL_CHOICES = (
        (1, '国家'),
        (2, '省/州'),
        (3, '市'),
        (4, '区/县'),
    )

    name = models.CharField(max_length=100, verbose_name='名称')
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, verbose_name='地址层级')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children',
                               verbose_name='上级地址')

    def __str__(self):
        if self.parent:
            return f"{self.name} ({self.get_level_display()}) - {self.parent.name}"
        return f"{self.name} ({self.get_level_display()})"

    class Meta:
        verbose_name = '地址'
        verbose_name_plural = '地址'
        ordering = ['level', 'name']


class Product(models.Model):
    """商品表"""
    STATUS_CHOICES = (
        (1, "未出售"),
        (2, "已出售"),
        (3, "已下架")
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="所属用户", related_name="products",
                             default=1)
    name = models.CharField(max_length=255, verbose_name='商品名称')
    description = models.TextField(blank=True, null=True, verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    under_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='降价后的价格', null=True,
                                      blank=True)
    stock = models.IntegerField(verbose_name='库存数量', default=1, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    shopping_address = models.CharField(max_length=128, verbose_name='发货地址', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='商品状态')
    sale_status = models.IntegerField(default=1, verbose_name='是否特卖', null=True, blank=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """照片表"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image_url = models.CharField(max_length=255, verbose_name='照片url')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    def __str__(self):
        return f"{self.product.name} - 图片"
