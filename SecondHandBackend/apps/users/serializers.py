import ast
import random
import string

from rest_framework import serializers
from SecondHandBackend.utils.id_generator import IdWorker
from SecondHandBackend.utils.password_encryption import encrypt_password, verify_password
from .models import UserProfile


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["mobile", "password"]

    def validate(self, data):
        mobile = data.get("mobile", "")
        password = data.get("password", "")
        if UserProfile.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError("该手机号已被注册!")
        hashed_password, password_salt = encrypt_password(password)
        user_id = self.get_user_id()
        name = self.get_user_name()
        data["user_id"] = user_id
        data["name"] = name
        data["username"] = name
        data['password'] = hashed_password
        data['password_salt'] = password_salt
        return data

    def get_user_id(self, datacenter_id=1, worker_id=1):
        """成成11随机数字id"""
        id_worker = IdWorker(datacenter_id, worker_id)
        return str(id_worker.get_id())[-11:]

    def get_user_name(self, length=8):
        """生成八位随机字符串姓名"""
        characters = string.ascii_letters + string.digits
        while True:
            username = ''.join(random.choices(characters, k=length))
            if not UserProfile.objects.filter(username=username).exists():
                return username


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["mobile", "password"]

    def validate(self, data):
        mobile = data.get("mobile", "")
        password = data.get("password", "")
        if not mobile or not password:
            raise serializers.ValidationError("未提供手机号和验证码")
        user_instance = UserProfile.objects.filter(mobile=mobile).first()
        if not user_instance:
            raise serializers.ValidationError("未找到该用户")
        hashed_password = user_instance.password
        password_salt = user_instance.password_salt
        hashed_password = ast.literal_eval(hashed_password)
        password_salt = ast.literal_eval(password_salt)
        verify_ret = verify_password(password, hashed_password, password_salt)
        if not verify_ret:
            raise serializers.ValidationError("密码错误")
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""

    class Meta:
        model = UserProfile
        fields = ['user_id', 'mobile', 'username', "email", "avatar_url", "birthday", "desc", "gender", "name",
                  'address']
