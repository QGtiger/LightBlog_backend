from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from article.models import Comment,ArticlePost


# Create your models here.
class Comment_reply(models.Model):
    comment_reply = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_reply")
    reply_type = models.IntegerField('回复0为主评论，1为子评论', default=0)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentator_reply")
    commented_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commented_user", blank=True, null=True)
    created = models.DateTimeField('评论时间', default=timezone.now)
    body = models.TextField('评论内容')
    reply_comment = models.IntegerField('评论评论的id', default=0)
    is_read = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
        verbose_name = ' 评论的评论 '
        verbose_name_plural = ' 评论的评论 '

    def __str__(self):
        return "Comment by {} on {}".format(self.comment_user, self.created)
