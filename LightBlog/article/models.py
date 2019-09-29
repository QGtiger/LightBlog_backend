from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
import os


# Create your models here.
class ArticleColumn(models.Model):
    user = models.ForeignKey(
        User,
        related_name='article_column',
        on_delete=models.CASCADE)
    column = models.CharField(' 栏目 ', max_length=200)
    created = models.DateTimeField(' 创建时间 ', auto_now_add=True)

    def __str__(self):
        return self.column

    class Meta:
        # 如果只设置verbose_name，在Admin中会显示“产品信息 s”
        verbose_name = ' 文章栏目 '
        verbose_name_plural = ' 文章栏目 '


def article_img_path(instance, filename):
    return os.path.join('previewBlog', str(instance.author.id), filename)


class ArticlePost(models.Model):
    author = models.ForeignKey(
        User,
        related_name='article_post',
        on_delete=models.CASCADE)
    title = models.CharField(' 文章标题 ', max_length=200)
    slug = models.SlugField(max_length=500)
    column = models.ForeignKey(
        ArticleColumn,
        on_delete=models.CASCADE,
        related_name='article_column')
    body = models.TextField(' 文章内容 ')
    word_count = models.IntegerField(' 文章字数 ', default=233)
    created = models.DateTimeField(' 创建时间 ', default=timezone.now)
    updated = models.DateTimeField(' 更新时间 ', auto_now=True)
    users_like = models.ManyToManyField(
        User, related_name="users_like", blank=True)
    image_preview = ProcessedImageField(
        upload_to=article_img_path,
        processors=[ResizeToFill(320, 260)],
        format='JPEG',
        options={'quality':98},
        default='default/preview.jpg',
        verbose_name='展示图片')

    class Meta:
        ordering = ("-updated",)
        index_together = (("id", "slug"),)
        verbose_name = ' 发布的文章 '
        verbose_name_plural = ' 发布的文章 '

    def __str__(self):
        return self.title

    def save(self, *args, **kargs):
        self.slug = slugify(self.title)
        super(ArticlePost, self).save(*args, **kargs)


class Comment(models.Model):
    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name="comments")
    commentator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="commentator")
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    comment_like = models.ManyToManyField(
        User, related_name="comment_like", blank=True)
    is_read = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
        verbose_name = ' 文章评论 '
        verbose_name_plural = ' 文章评论 '

    def __str__(self):
        return "Comment by {} on {}".format(self.commentator, self.created)


class Carousel(models.Model):
    title = models.CharField(
        '图片标题',
        max_length=50,
        blank=True,
        null=True,
        default='LightBlog niubility')
    image = ProcessedImageField(
        upload_to='Carousel',
        processors=[ResizeToFill(937, 405)],
        format='JPEG',
        options={'quality':98}, verbose_name='展示图片')

    image_130x56 = ImageSpecField(
        source="image",
        processors=[ResizeToFill(130, 56)],  # 处理后的图像大小
        format='JPEG',  # 处理后的图片格式
        options={'quality': 90}  # 处理后的图片质量
    )

    class Meta:
        # 如果只设置verbose_name，在Admin中会显示“产品信息 s”
        verbose_name = ' 轮播图 '
        verbose_name_plural = ' 轮播图 '
