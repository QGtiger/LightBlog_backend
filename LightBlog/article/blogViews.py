from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost, Comment,LightBlogSpecialColumn,LightBlogSpecialTheme,LightBlogPersonalColumn,LightBlogArticle, LightBlogArticleImage
from comment.models import Comment_reply
from .tasks import *
import json
import redis
import re
import os
import time
import jwt
from django.conf import settings
import datetime
from django.core.files.base import ContentFile
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

# 获取用户   token = request.META.get('HTTP_AUTHORIZATION')
def getUser(token):
    dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    user = User.objects.get(username=username)
    return user


def nullParam():
    return HttpResponse(json.dumps({"success": False, 'tips': "参数不能为空"}))


def isSuperUser(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    user = User.objects.get(username=username)
    if not user.is_superuser:
        return HttpResponse(json.dumps({"success": False, 'tips': "您没有权限"}))


@csrf_exempt
def blog_detail(request):
    try:
        id = request.POST.get('id', nullParam())
        blog = LightBlogArticle.objects.get(id=id)
        view = r.get('lightblog:{}:views'.format(id))
        if view is None:
            view_count = 0
        else:
            view_count = view.decode('utf-8')
        data = {"id": blog.id,
                         "title": blog.title,
                         "description": blog.article_descripton,
                         "specialColumn": blog.specialColumn.special_column,
                         "specialColumnId":blog.specialColumn.id,
                         "specialTheme": blog.specialTheme.special_theme,
                         "specialThemeId": blog.specialTheme.id,
                         "created": time.mktime(blog.created.timetuple()),
                         "updated": time.mktime(blog.updated.timetuple()),
                         "isRecommend": blog.isRecommend,
                         "usersLike": blog.users_like.count(),
                         "usersDisLike": blog.users_dislike.count(),
                         "scanCount": view_count,
                         "author": blog.author.username,
                            "status": blog.article_status,
                         "wordCount": blog.article_wordCount,
                        "body": blog.article_body,}
        return HttpResponse(json.dumps({"success": True, "data":data, "tips": 'ok'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))