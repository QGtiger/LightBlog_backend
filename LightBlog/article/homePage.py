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


# 获取首页文章
@csrf_exempt
def get_articles(request):
    try:
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 10)
        articleList = LightBlogArticle.objects.filter(isRecommend=True).filter(article_status=3).order_by('-checkTime')
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
            view = r.get('lightblog:{}:views'.format(list[i].id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
            articles.append({"id": list[i].id,
                             "title": list[i].title,
                             "description": list[i].article_descripton,
                             "specialColumn": list[i].specialColumn.special_column,
                             "specialColumnId": list[i].specialColumn.id,
                             "specialTheme": list[i].specialTheme.special_theme,
                             "specialThemeId": list[i].specialTheme.id,
                             "personalColumn": list[i].personalColumn.personal_column,
                             "created": time.mktime(list[i].created.timetuple()),
                             "updated": time.mktime(list[i].updated.timetuple()),
                             "checked": time.mktime(list[i].checkTime.timetuple()) if list[i].checkTime else '',
                             "usersLike": list[i].users_like.count(),
                             "usersDisLike": list[i].users_dislike.count(),
                             "scanCount": view_count,
                             "wordCount": list[i].article_wordCount,
                             "body": init_blog(list[i].article_body)[:200],
                             'blog_img_url': list[i].article_preview.url,
                             'author_img_url': list[i].author.userinfo.photo_150x150.url,
                             'author': list[i].author.username})
        return HttpResponse(json.dumps({"success": True, "data": articles, "total": len(articleList), "totalPage": paginator.num_pages}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))
