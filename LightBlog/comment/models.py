from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from article.models import ArticlePost,LightBlogArticle


class LightBlogComment(models.Model):
    article = models.ForeignKey(
        LightBlogArticle,
        on_delete=models.CASCADE,
        related_name='lightblog_comment'
    )
    commentator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="commentator"
    )
    comment_text = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    comment_like = models.ManyToManyField(
        User,
        related_name="comment_like",
        blank=True
    )
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    reported_text = models.TextField(blank=True,null=True)
    deleted_by_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)


class LightBlogComment_reply(models.Model):
    comment_reply = models.ForeignKey(
        LightBlogComment,
        on_delete=models.CASCADE,
        related_name="lightblogcomment_reply"
    )
    reply_type = models.IntegerField('0 为主评论， 1为子评论', default=0)
    comment_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_user"
    )
    commented_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="commented_user"
    )
    created = models.DateTimeField(default=timezone.now)
    comment_text = models.TextField()
    reply_comment = models.IntegerField('评论 评论的id', default=0)
    comment_like = models.ManyToManyField(
        User,
        related_name="comment_reply_like",
        blank=True
    )
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    reported_text = models.TextField(blank=True,null=True)
    deleted_by_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)



