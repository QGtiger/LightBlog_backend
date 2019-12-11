from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from .models import ArticlePost

@shared_task
def article_post_task(title, body, column_id, username):
    user = User.objects.get(username=username)
    column = user.article_column.get(id=column_id)
    article = ArticlePost(author=user, title=title, body=body, column=column)
    article.save()
    return '{} 文章上传'.format(title)

