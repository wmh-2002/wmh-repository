from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import CartItem, Product
from .serializers import CartItemSerializer
from SecondHandBackend.utils.return_code import StatusCodeEnum


class CartViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  viewsets.GenericViewSet,
                  mixins.ListModelMixin, mixins.DestroyModelMixin):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all().order_by('-id')

    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """列出购物车中的所有商品"""
        cart_items = self.get_queryset()
        serializer = CartItemSerializer(cart_items, many=True)
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": serializer.data
        }
        return Response(resp, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """添加商品到购物车"""
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        """更新购物车中的商品数量"""
        cart_item = CartItem.objects.get(id=pk, user=request.user)
        quantity = request.data.get('quantity')

        # 检查商品库存
        if cart_item.product.stock < quantity:
            return Response({'error': '库存不足'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)

    def destroy(self, request, *args, **kwargs):
        """删除购物车中的某个商品"""
        pass
