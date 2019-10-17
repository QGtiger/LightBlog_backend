from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost, Comment,LightBlogSpecialColumn,LightBlogSpecialTheme,LightBlogPersonalColumn
from comment.models import Comment_reply
from django.conf import settings
from .tasks import *
import json
import redis
import re
import time
import jwt
from django.conf import settings
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

# 获取用户   token = request.META.get('HTTP_AUTHORIZATION')
def getUser(token):
    dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    user = User.objects.get(username=username)
    return user


# 获取用户文章
@csrf_exempt
def get_articles(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        user = getUser(token)
        articleList = user.lightblog_article.all()
        page = request.GET.get('page', '')
        size = request.GET.get('size', '')
        paginator = Paginator(articleList, size)
        try:
            current_page = paginator.page(page)
            list = current_page.object_list
        except PageNotAnInteger:
            current_page = paginator.page(1)
            list = current_page.object_list
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)
            list = current_page.object_list
        articles = []
        for i in range(len(list)):
            articles.append({"id": list[i].id,
                             "title": list[i].title,
                             "description": list[i].article_descripton,
                             "specialColumn": list[i].specialColumn.special_column,
                             "specialColumnId":list[i].specialColumn.id,
                             "specialTheme": list[i].specialTheme.special_theme,
                             "specialThemeId": list[i].specialTheme.id,
                             "personalColumn": list[i].personalColumn.personal_column,
                             "created": time.mktime(list[i].created.timetuple()),
                             "updated": time.mktime(list[i].updated.timetuple()),
                             "isRecommend": list[i].isRecommend,
                             "usersLike": list[i].users_like.count(),
                             "usersDisLike": list[i].users_dislike.count(),
                                "status": list[i].article_status})
        return HttpResponse(json.dumps({"success": True, "data": articles, "total": len(articleList)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))