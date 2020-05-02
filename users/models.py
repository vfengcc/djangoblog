import hashlib
import os

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):

    name = models.CharField(max_length=30, null=True, blank=True, verbose_name='姓名')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    sex = models.CharField(max_length=6, choices=(('man', '男'), ('woman', '女')), default='woman', verbose_name='性别')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机')
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name='邮箱')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_userext(self):
        return UserExt.objects.get(user_id=self.pk)

class UserExt(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    nickname = models.CharField(max_length=64, verbose_name='昵称')
    avatar = models.CharField(max_length=256, verbose_name='头像')
    score = models.PositiveIntegerField(default=0, verbose_name='发帖数')
    logintime = models.DateTimeField(auto_now_add=True)
    validkey = models.CharField(max_length=256, verbose_name='激活key')
    status = models.IntegerField(default=0, verbose_name='状态')

    class Meta:
        verbose_name = '用户扩展'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname

    __repr__ = __str__

    def nickname_text(self):
        return self.user.name if self.nickname == '' else self.nickname

    @classmethod
    def gen_validkey(cls):
        m = hashlib.md5()
        m.update(os.urandom(32))
        return m.hexdigest()