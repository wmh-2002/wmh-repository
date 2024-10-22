from django.db import models
from SecondHandBackend.apps.users.models import UserProfile
from SecondHandBackend.apps.product.models import Product


# Create your models here.


class CartItem(models.Model):
    """购物车item"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # 商品数量
    added_at = models.DateTimeField(auto_now_add=True)  # 添加时间

    def get_total_price(self):
        return self.product.price * self.quantity  # 计算该购物车项的总价
