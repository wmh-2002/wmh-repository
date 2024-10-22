import base64
import os
import re
import uuid
from datetime import datetime
from io import BytesIO
import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

from SecondHandBackend import settings
from SecondHandBackend.apps.users.serializers import UserLoginSerializer, UserDetailSerializer, UserRegisterSerializer
from SecondHandBackend.utils.code import check_code
from SecondHandBackend.utils.return_code import StatusCodeEnum
from .models import UserProfile
from SecondHandBackend.utils.common_logger import logger


# Create your views here.

class UserPageNumberPagination(PageNumberPagination):
    """用户列表分页"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 40


class UserFilter(django_filters.FilterSet):
    """商品如按照name关键字搜索过滤"""
    role = django_filters.CharFilter(field_name='role')
    username = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    mobile = django_filters.CharFilter(field_name='mobile')

    class Meta:
        model = UserProfile
        fields = ["username"]


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet,
                  mixins.ListModelMixin, mixins.DestroyModelMixin):
    serializer_class = UserDetailSerializer
    queryset = UserProfile.objects.all().order_by('created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    pagination_class = UserPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        users = self.filter_queryset(queryset)
        count = len(users)
        page = self.paginate_queryset(users)
        serializer = self.get_serializer(page, many=True)
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": {
                "data": serializer.data,
                "count": count
            }
        }
        return Response(resp, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """查找单个用户实例"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_permissions(self):
        """

        :return: 获取权限类
        """
        if self.request.method.lower() in ['post', 'get']:
            return []
        else:
            return [IsAuthenticated()]

    def get_authenticators(self):
        """

        :return: 获取认证类
        """
        if self.request.method.lower() in ['post', 'get']:
            return []
        else:
            return [JWTAuthentication(), SessionAuthentication()]

    def create(self, request, *args, **kwargs):
        """
        用户登录注册视图函数
        :param request:前端发来的用户请求
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.data
        is_new_user = request_data.pop('is_new_user', False)
        # 注册
        if is_new_user:
            serializer = UserRegisterSerializer(data=request_data)
            if not serializer.is_valid():
                resp = {
                    "code": StatusCodeEnum.ERROR.value[0],
                    "message": StatusCodeEnum.ERROR.value[1],
                    "data": {
                        "error": serializer.errors['non_field_errors'][0]
                    }
                }
                return Response(resp, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            resp = {
                "code": StatusCodeEnum.OK.value[0],
                "message": StatusCodeEnum.OK.value[1],
            }
            return Response(resp, status=status.HTTP_201_CREATED)
        # 登录
        serializer = UserLoginSerializer(data=request_data)
        if not serializer.is_valid():
            resp = {
                "code": StatusCodeEnum.ERROR.value[0],
                "message": StatusCodeEnum.ERROR.value[1],
                "data": {
                    "error": serializer.errors['non_field_errors'][0]
                }
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        mobile = serializer.validated_data.get('mobile', "")
        user_instance = UserProfile.objects.filter(mobile=mobile).first()
        last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_instance.last_login = last_login
        user_instance.save()
        re_dict = self.get_token(user_instance)
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": {
                "re_dict": re_dict
            }
        }
        return Response(resp, status=status.HTTP_200_OK)

    def get_token(self, user_instance):
        """
        返回用户的基本信息
        :param user_instance: 用户实例
        :return:
        """
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        serializer = UserDetailSerializer(instance=user_instance)
        re_dict = serializer.data

        re_dict['access_token'] = access_token
        re_dict['refresh_token'] = refresh_token
        return re_dict

    def destroy(self, request, *args, **kwargs):
        """

        :param request: 前端用户发起请求
        :param args:
        :param kwargs:
        :return:
        """
        user_instance = self.get_object()
        avatar_url = user_instance.avatar_url
        if avatar_url:
            avatar_save_path = self.ger_image_save_path(avatar_url)
            os.remove(avatar_save_path)
        user_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        if request.FILES:
            file_name = request.FILES['file']
            image_name = request.FILES['file'].name
            image_id = str(uuid.uuid4()) + '.' + image_name.split('.')[-1]
            save_path = os.path.join(settings.MEDIA_ROOT, image_id).replace("\\", '/')
            # 保存图片到指定路径
            with open(save_path, 'wb') as f:
                # .chunks()为图片的一系列数据，它是一段段的，所以要用for逐个读取
                for content in file_name.chunks():
                    f.write(content)
            avatar_url = self.get_image_url(save_path)
            user_instance = request.user
            if user_instance.avatar_url:
                old_avatar_url = user_instance.avatar_url
                old_avatar_save_path = self.ger_image_save_path(old_avatar_url)
                os.remove(old_avatar_save_path)
            user_instance.avatar_url = avatar_url
            user_instance.save()
            self.ger_image_save_path(avatar_url)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        user_serializer = UserDetailSerializer(instance=instance)

        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1],
            "data": {
                "data": user_serializer.data
            }
        }
        return Response(resp, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def update_role(self, request):
        """
        更新用户角色
        :param request:
        :return:
        """
        user_id = request.data.get('user_id', "")
        user_instance = UserProfile.objects.filter(user_id=user_id).first()
        if not user_instance:
            resp = {
                "code": StatusCodeEnum.ERROR.value[0],
                "message": StatusCodeEnum.ERROR.value[1],
                "data": {
                    "error": "未找到该用户"
                }
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        role = request.data.get('role', "")
        if not role:
            resp = {
                "code": StatusCodeEnum.ERROR.value[0],
                "message": StatusCodeEnum.ERROR.value[1]
            }
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        user_instance.role = role
        user_instance.save()
        resp = {
            "code": StatusCodeEnum.OK.value[0],
            "message": StatusCodeEnum.OK.value[1]
        }
        return Response(resp, status=status.HTTP_200_OK)

    def ger_image_save_path(self, url):
        match = re.search(r'media/(.+)', url)
        key = match.group(1)
        return settings.MEDIA_ROOT + "/" + key

    def get_image_url(self, save_path):
        base_url = "http://127.0.0.1:8000/"
        match = re.search(r'media/(.+)', save_path)
        key = match.group(1)
        return base_url + "media/" + key

    @action(methods=['get'], detail=False)
    def getCode(self, request, *args, **kwargs):
        """
        :return: 图片验证码的url
        """
        img, code_string = check_code()
        # 写入到自己的session中，一遍后期获取验证码，进行效验
        request.session["image_code"] = code_string
        # 给session设置六十秒超时
        request.session.set_expiry(600)
        stream = BytesIO()
        img.save(stream, 'png')

        # 将验证码图片转换为 base64 编码
        img_base64 = base64.b64encode(stream.getvalue()).decode('utf-8')

        # 返回验证码图片的 base64 编码和验证码字符串
        response_data = {
            'image': img_base64,
            'code_string': code_string
        }
        # 将 JSON 数据返回给客户端
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def refreshToken(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            # 只生成新的访问令牌
            new_access_token = str(refresh.access_token)
            return Response({
                "access": new_access_token
            }, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"error": "Invalid refresh token"}, status=400)
