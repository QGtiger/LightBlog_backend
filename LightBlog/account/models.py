from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
import os


def lightblog_authorbg(instance, filename):
    return os.path.join('avator', str(instance.user.id), filename)

# Create your models here.
class UserInfo(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userinfo',
        unique=True)
    school = models.CharField(' 学校 ', max_length=100, blank=True)
    company = models.CharField(' 在职公职 ', max_length=100, blank=True)
    profession = models.CharField(' 工作 ', max_length=100, blank=True)
    address = models.CharField(' 地址 ', max_length=100, blank=True)
    aboutme = models.TextField(' 自我介绍 ', blank=True)
    photo = ProcessedImageField(
        upload_to=lightblog_authorbg,
        processors=[ResizeToFill(400, 400)],
        format='JPEG',
        options={'quality':98},
        default='default/default.jpg',
        verbose_name='展示图片')
    user_bg = ProcessedImageField(
        upload_to=lightblog_authorbg,
        processors=[ResizeToFill(800, 300)],
        format='JPEG',
        options={'quality':98},
        default='default/author-bg.jpg',
        verbose_name='展示图片')

    # 注意：ImageSpecField不会生成数据库中的表
    # 处理后的图片
    photo_150x150 = ImageSpecField(
        source="photo",
        processors=[ResizeToFill(30, 30)],  # 处理后的图像大小
        format='JPEG',  # 处理后的图片格式
        options={'quality': 95}  # 处理后的图片质量
    )

    photo_100x100 = ImageSpecField(
        source="photo",
        processors=[ResizeToFill(100, 100)],  # 处理后的图像大小
        format='JPEG',  # 处理后的图片格式
        options={'quality': 90}  # 处理后的图片质量
    )

    def __str__(self):
        return "User:{}".format(self.user.username)

    class Meta:
        # 如果只设置verbose_name，在Admin中会显示“产品信息 s”
        verbose_name = ' 用户信息 '
        verbose_name_plural = ' 用户信息 '


class UserToken(models.Model):
    user = models.OneToOneField(User, related_name='userToken', on_delete=models.CASCADE, unique=True)
    token = models.CharField(max_length=200, blank=True)