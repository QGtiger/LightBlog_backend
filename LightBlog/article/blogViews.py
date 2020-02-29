from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost, LightBlogSpecialColumn,LightBlogSpecialTheme,LightBlogPersonalColumn,LightBlogArticle, LightBlogArticleImage
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

def init_blog(content):
    content_text1 = content.replace(
        '<p>',
        '').replace(
        '</p>',
        '').replace(
            "'",
        '')
    # 去掉图片链接
    content_text2 = re.sub(r'(!\[.*?\]\(.*?\))', '', content_text1)
    # 去掉markdown标签
    pattern = r'[\\\`\*\_\[\]\#\+\-\!\>]'
    content_text3 = re.sub(pattern, '', content_text2)
    return content_text3

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
        view = r.incr('lightblog:{}:views'.format(id))
        r.zincrby('lightblog_ranking', 1, id)    #view.decode('utf-8')
        recommendBlogs = list(blog.author.lightblog_article.filter(isRecommend=True))[:3]

        recommendBlogsList = []
        for i in range(len(recommendBlogs)):
            viewCount = r.get('lightblog:{}:views'.format(recommendBlogs[i].id))
            recommendBlogsList.append({
                "title": recommendBlogs[i].title,
                "updated": time.mktime(recommendBlogs[i].updated.timetuple()),
                "usersLike": recommendBlogs[i].users_like.count(),
                "scanCount": 0 if viewCount is None else viewCount.decode('utf-8'),
                "id": recommendBlogs[i].id
            })
        if view is None:
            view_count = 0
        else:
            view_count = view
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
                "author_url": blog.author.userinfo.photo_150x150.url,
                "author_100x100": blog.author.userinfo.photo_100x100.url,
                "author_blogsCount": blog.author.lightblog_article.filter(isRecommend=True).count(),
                "author_recommendBlogsList": recommendBlogsList,
                    "status": blog.article_status,
                 "wordCount": blog.article_wordCount,
                "body": blog.body_html,}
        blog_author = blog.author
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        current_user = User.objects.get(username=username)
        followed_users = current_user.userinfo.user_follow.all()
        is_follow = False
        for item in followed_users:
            if item == blog_author:
                is_follow = True
        return HttpResponse(json.dumps({"success": True,"is_collected": current_user in blog.collector.all() ,"data":data, "tips": 'ok', "is_follow": is_follow, "is_like": current_user in blog.users_like.all(), 'is_dislike': current_user in blog.users_dislike.all()}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))

