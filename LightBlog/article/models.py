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


def lightblog_articleimgs(instance, filename): # 文章内图片
    return os.path.join('LightBlogArticleImages', str(instance.article.id), filename)


def lightblog_articleimgscompress(instance, filename): #文章内压缩 图片
    return os.path.join('LightBlogArticleImagesCompress', str(instance.article.id), filename)


def lightblog_articleimgspreview(instance, filename): #文章内压缩 图片
    return os.path.join('LightBlogArticleImagesPreview', str(instance.article.id), filename)


def lightblog_specialcolumn(instance, filename):
    return os.path.join('SpecialColumn', str(instance.id), filename)


def lightblog_specialtheme(instance, filename):
    return os.path.join('SpecialTheme', str(instance.id), filename)

def lightblog_personalcolumn(instance, filename):
    return os.path.join('PersonalColumn', str(instance.create_user.id), filename)


def lightblog_articlepreview(instance, filename):
    return os.path.join('LightBlogArticlePreview', str(instance.id), filename)


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


class LightBlogSpecialColumn(models.Model):
    create_user = models.ForeignKey(
        User,
        related_name='lightblog_specialcolumn',
        on_delete=models.CASCADE
    )
    special_column = models.CharField(' 专栏名称 ', max_length=50)
    created = models.DateTimeField(' 创建时间 ', default=timezone.now)
    description = models.CharField(' 专栏简介 ', max_length=100)
    isPublish = models.IntegerField(' 是否发布 ', default=0)
    image_preview = ProcessedImageField(
        upload_to=lightblog_specialcolumn,
        processors=[ResizeToFill(240, 240)],
        format='JPEG',
        options={'quality':98},
        default='default/preview.jpg',
        verbose_name='展示图片')

    class Meta:
        ordering = ("-created",)


class LightBlogSpecialTheme(models.Model):
    create_user = models.ForeignKey(
        User,
        related_name='lightblog_specialtheme',
        on_delete=models.CASCADE
    )
    special_column = models.ForeignKey(
        LightBlogSpecialColumn,
        related_name='lightblog_specialcolumn',
        on_delete=models.CASCADE
    )
    special_theme = models.CharField(' 专题名称 ', max_length=50)
    created = models.DateTimeField(' 创建时间 ', default=timezone.now)
    description = models.CharField(' 专题简介 ', max_length=100)
    isPublish = models.IntegerField(' 是否发布 ', default=0)
    image_preview = ProcessedImageField(
        upload_to=lightblog_specialtheme,
        processors=[ResizeToFill(240, 240)],
        format='JPEG',
        options={'quality':98},
        default='default/preview.jpg',
        verbose_name='展示图片')

    class Meta:
        ordering = ("-created",)


class LightBlogPersonalColumn(models.Model):
    create_user = models.ForeignKey(
        User,
        related_name='lightblog_personalcolumn',
        on_delete=models.CASCADE
    )
    personal_column = models.CharField(' 个人栏目 ', max_length=20)
    created = models.DateTimeField(' 创建时间 ', default=timezone.now)
    description = models.CharField(' 栏目简介 ', max_length=100)
    status = models.IntegerField(' 栏目显示 ', default=1)  # 是否显示在自己的页面， 1 显示 0 不显示
    image_preview = ProcessedImageField(
        upload_to=lightblog_personalcolumn,
        processors=[ResizeToFill(240, 240)],
        format='JPEG',
        options={'quality':98},
        default='default/preview.jpg',
        verbose_name='展示图片')

    class Meta:
        ordering = ("-created",)


class LightBlogArticle(models.Model):
    author = models.ForeignKey(
        User,
        related_name='lightblog_article',
        on_delete=models.CASCADE
    )
    title = models.CharField(' 文章标题 ', max_length=50)
    specialColumn = models.ForeignKey(
        LightBlogSpecialColumn,
        related_name='article_specialcolumn',
        on_delete=models.CASCADE
    )
    specialTheme = models.ForeignKey(
        LightBlogSpecialTheme,
        related_name='article_specialtheme',
        on_delete=models.CASCADE
    )
    personalColumn = models.ForeignKey(
        LightBlogPersonalColumn,
        related_name='article_personalcolumn',
        on_delete=models.CASCADE
    )
    article_status = models.IntegerField(default=0) # 文章状态 1 待处理， 2已驳回  3 已通过 0 草稿，默认是草稿
    checkTime = models.DateTimeField(' 审核时间 ', null=True, blank=True)
    checkText = models.CharField(' 审核内容 ', max_length=300, default="")
    created = models.DateTimeField(' 创建时间 ', default=timezone.now)
    updated = models.DateTimeField(' 更新时间 ', auto_now=True)
    article_body = models.TextField(' 文章内容 ')
    body_html = models.TextField(' Html 内容 ', default=" 默认 ")
    article_wordCount = models.IntegerField(' 文章字数 ', default=233)
    article_preview = ProcessedImageField(
        upload_to=lightblog_articlepreview,
        processors=[ResizeToFill(320, 320)],
        format='JPEG',
        options={'quality':98},
        default='default/preview.jpg',
        verbose_name='展示图片')
    article_descripton = models.CharField(' 文章简介 ', max_length=200)
    isRecommend = models.BooleanField(' 是否推荐 ', default=False)
    users_like = models.ManyToManyField(
        User, related_name="lightblog_users_like", blank=True)
    users_dislike = models.ManyToManyField(
        User, related_name="lightblog_users_dislike", blank=True)

    class Meta:
        ordering = ("-updated",)




class LightBlogArticleImage(models.Model):
    article = models.ForeignKey(
        LightBlogArticle,
        on_delete=models.CASCADE,
        related_name="lightblog_articleimage"
    )
    image = models.ImageField(upload_to=lightblog_articleimgs, blank=True, null=True)
    imageCompress = models.ImageField(upload_to=lightblog_articleimgscompress, blank=True, null=True)


# 文章审核回复模板
class LightBlogReplyTemplate(models.Model):
    title = models.CharField(' 回复模板标题 ', max_length=50)
    content = models.CharField(' 回复模板内容 ', max_length=500)





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
