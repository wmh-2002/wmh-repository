from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class UserProfile(AbstractUser):
    GENDER_CHOICES = (
        (0, "女"),
        (1, "男"),
        (2, "未知")
    )
    user_id = models.CharField(max_length=64, primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    password_salt = models.CharField(max_length=128, null=True, blank=True)
    mobile = models.CharField(max_length=11, blank=True)
    email = models.CharField(max_length=128, null=True, blank=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=2, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar_url = models.CharField(max_length=128, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name
