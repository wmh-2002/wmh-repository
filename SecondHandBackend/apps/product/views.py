import os
import uuid

import django_filters
from django.contrib.auth.models import AnonymousUser
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from SecondHandBackend import settings
from SecondHandBackend.utils.return_code import StatusCodeEnum, ReturnCodeEnum
from SecondHandBackend.apps.product.serializer import CategorySerializer, AddressSerializer, ProductSerializer, \
    AddProductSerializer

from SecondHandBackend.apps.product.models import Category, Address, Product, ProductImage
from SecondHandBackend.utils.saveImages import get_image_url, ger_image_save_path
from SecondHandBackend.utils.common_logger import logger


# Create your views here.

class ProductPageNumberPagination(PageNumberPagination):
    """商品列表分页"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 40


class ProductFilter(django_filters.FilterSet):
    """商品如按照name关键字搜索过滤"""
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    sale_status = django_filters.CharFilter(field_name='sale_status')

    # category = django_filters.CharFilter(Field='category')

    class Meta:
        model = Product
        fields = ["name"]


class CategoryViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      viewsets.GenericViewSet,
                      mixins.ListModelMixin, mixins.DestroyModelMixin):
    """商品分类视图类"""
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('created_at')

    def list(self, request, *args, **kwargs):
        """
        全部分类
        :param request: 前端发起请求
        :param args:
        :param kwargs:
        :return:所有分类
        """
        amount = request.query_params.get('amount', "")
        categories = self.queryset.all()
        if not amount:
            categories = categories.filter(parent__isnull=True)
        serializer = self.get_serializer(categories, many=True)
        resp = {
            'code': StatusCodeEnum.OK.value[0],
            'message': StatusCodeEnum.OK.value[1],
            'data': serializer.data
        }
        return Response(resp, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        创建新的分类
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            resp = {
                "code": StatusCodeEnum.ERROR.value[0],
                "message": StatusCodeEnum.ERROR.value[1]
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": serializer.data
        }
        return Response(resp, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        category = self.get_object()
        category.delete()
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1]
        }
        return Response(resp, status=status.HTTP_204_NO_CONTENT)


class AddressViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                     viewsets.GenericViewSet,
                     mixins.ListModelMixin, mixins.DestroyModelMixin):
    """地址视图类"""
    serializer_class = AddressSerializer
    queryset = Address.objects.all().order_by('-id')
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        全部分类
        :param request: 前端发起请求
        :param args:
        :param kwargs:
        :return:所有分类
        """
        addresses = self.queryset.all().filter(parent__isnull=True)
        serializer = self.get_serializer(addresses, many=True)
        resp = {
            'code': StatusCodeEnum.OK.value[0],
            'message': StatusCodeEnum.OK.value[1],
            'data': serializer.data
        }
        return Response(resp, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        创建新的地址
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            resp = {
                "code": StatusCodeEnum.ERROR.value[0],
                "message": StatusCodeEnum.ERROR.value[1]
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": serializer.data
        }
        return Response(resp, status=status.HTTP_201_CREATED)


class ProductViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                     viewsets.GenericViewSet,
                     mixins.ListModelMixin, mixins.DestroyModelMixin):
    """商品视图类"""
    serializer_class = ProductSerializer
    # queryset = Product.objects.all().order_by('-created_at')
    queryset = Product.objects.all().order_by('created_at')
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = ProductPageNumberPagination

    def get_permissions(self):
        """
        获取权限类
        :return:
        """
        if self.action == 'list':
            return []
        else:
            return [IsAuthenticated()]

    def get_serializer_class(self):
        """获取序列器"""
        if self.action == "list":
            return ProductSerializer
        else:
            return AddProductSerializer

    def create(self, request, *args, **kwargs):
        """
        创建商品
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        user = request.user
        request_data = request.data
        images = request_data.pop('images', None)
        shopping_address = request_data.get('shopping_address', None)
        address = self.get_address(shopping_address)
        mutable_query_dict = request_data.copy()
        mutable_query_dict['shopping_address'] = address
        logger.info(user.user_id)
        mutable_query_dict['user'] = user.user_id
        serializer = self.get_serializer(data=mutable_query_dict)
        if not serializer.is_valid():
            resp = {
                "code": StatusCodeEnum.ERROR.value[0],
                "message": StatusCodeEnum.ERROR.value[1]
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        logger.info(serializer.validated_data)
        product_instance = serializer.save()
        product_id = product_instance.id
        if images:
            ret_code = self.save_images_to_local(images, product_id)
            if ret_code == StatusCodeEnum.OK.value[0]:
                resp = {
                    "code": StatusCodeEnum.OK.value[0],
                    "message": StatusCodeEnum.OK.value[1],
                }
                return Response(resp, status=status.HTTP_201_CREATED)
            resp = {
                "code": StatusCodeEnum.ERROR.value[0],
                "message": StatusCodeEnum.ERROR.value[1],
                "data": {
                    "error": "存储照片失败"
                }
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    def save_images_to_local(self, images, product_id):
        """
        将照片保存至本地并更新数据库
        :param images: 图片文件列表
        :param product_id: 关联的产品 ID
        :return: 成功或失败状态码
        """
        try:
            for image in images:
                # 生成唯一的文件名
                image_name = image.name
                image_extension = image_name.split('.')[-1]
                image_id = f"{uuid.uuid4()}.{image_extension}"
                save_path = os.path.join(settings.MEDIA_ROOT, image_id)

                # 保存图片到指定路径
                with open(save_path, 'wb') as f:
                    for content in image.chunks():
                        f.write(content)

                # 获取图片的 URL 并保存数据库
                image_url = get_image_url(save_path)
                ProductImage.objects.create(
                    product_id=product_id,
                    image_url=image_url
                )

            return ReturnCodeEnum.OK.value[0]

        except Exception as e:
            logger.error(f"Error saving image for product {product_id}: {e}")
            Product.objects.filter(id=product_id).delete()
            return -1

    def get_address(self, address_list):
        """
        根据id列表获取地址名字
        :param address_list:
        :return:
        """
        shopping_address_list = [item.strip() for item in address_list.split(',')]
        address_name = ""
        for id in shopping_address_list:
            address = Address.objects.filter(id=id).first()
            address_name += address.name
        return address_name

    def list(self, request, *args, **kwargs):
        """查询全部商品"""
        user = request.user
        request_params = request.query_params
        amount = request_params.get('amount', None)
        category = request_params.get('category', None)
        max_price = request_params.get('max_price', None)
        min_price = request_params.get('min_price', None)

        # 匿名用户或带有 'amount' 参数的请求，查询所有商品
        if isinstance(user, AnonymousUser) or amount:
            products = self.queryset.all()  # 查询所有商品
        else:
            # 登录用户，查询其发布的商品
            products = self.queryset.filter(user=user)
        # 过滤查找
        products = self.filter_queryset(products)
        if max_price and min_price:
            # price__gte=100：表示价格大于或等于 100。
            # price__lte=500：表示价格小于或等于 500。
            products = products.filter(price__gte=min_price, price__lte=max_price)
        if category:
            last_level_categories = self.get_last_level_category(category)
            if last_level_categories:
                category_ids = [item.get('id') for item in last_level_categories]
                if category_ids[0] != 5:
                    products = products.filter(category_id__in=category_ids)  # 使用 __in 来过滤
            else:
                products = products.none()
        # 进行分页
        page = self.paginate_queryset(products)
        # 序列化商品列表
        serializer = ProductSerializer(page, many=True)
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": {
                "products": serializer.data,
                "total": len(products)
            }
        }
        return Response(resp, status=status.HTTP_200_OK)

    def get_last_level_category(self, category):
        """获取分类实例的最后一级分类"""

        # 从数据库获取分类实例
        category_instance = Category.objects.filter(id=category).first()

        if not category_instance:
            return None  # 如果分类不存在，返回 None 或根据需求抛出异常

        # 序列化分类实例
        serializer = CategorySerializer(category_instance)

        # 用于存储所有最后一级分类
        last_level_categories = []

        # 递归查找最后一级分类
        def find_last_level_category(category_data):
            children = category_data.get("children", [])
            if not children:
                # 如果没有子分类，这就是最后一级分类
                last_level_categories.append(category_data)
                return
            # 如果有子分类，递归查找
            for child in children:
                find_last_level_category(child)

        # 获取顶级分类的数据
        category_data = serializer.data

        # 查找最后一级分类
        find_last_level_category(category_data)
        return last_level_categories  # 返回所有最后一级分类

    def destroy(self, request, *args, **kwargs):
        """
        :param request: 前端用户发起delete请求
        :param args:
        :param kwargs:
        :return:
        """
        product_instance = self.get_object()
        product_images = product_instance.images.all()
        for image in product_images:
            image_url = image.image_url
            image_save_path = ger_image_save_path(image_url)
            os.remove(image_save_path)
            image.delete()
        product_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        商品更新接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        update_data = request.data
        instance.name = update_data.get('name')
        instance.description = update_data.get('description')
        instance.price = update_data.get('price')
        instance.shopping_address = update_data.get('shopping_address')
        instance.save()
        serializer = ProductSerializer(instance=instance)
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": {
                "data": serializer.data
            }
        }
        return Response(resp, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def discount(self, request, *args, **kwargs):
        """
        一键降价视图
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        data = request.data
        discounted_price = data.get('discounted_price', "")
        price = instance.price
        new_price = float(price) - float(discounted_price)
        instance.under_price = new_price
        instance.sale_status = 2
        instance.save()
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
        }
        return Response(resp, status=status.HTTP_200_OK)
