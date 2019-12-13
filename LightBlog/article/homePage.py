from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost,LightBlogSpecialColumn,LightBlogSpecialTheme,LightBlogPersonalColumn,LightBlogArticle, LightBlogArticleImage
from django.db.models import Q
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
    content_text1 = re.sub(r'<.*?>', '', content_text1)
    # 去掉图片链接
    content_text2 = re.sub(r'(!\[.*?\]\(.*?\))', '', content_text1)
    # 去掉markdown标签
    pattern = r'[\\\`\*\_\[\]\#\+\-\!\>]'
    content_text3 = re.sub(pattern, '', content_text2)
    content_text3 = content_text3.replace('\n', '')
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
                             "body": init_blog(list[i].body_html)[:200],
                             'blog_img_url': list[i].article_preview.url,
                             'author_img_url': list[i].author.userinfo.photo_150x150.url,
                             'author': list[i].author.username})
        return HttpResponse(json.dumps({"success": True, "data": articles, "total": len(articleList), "totalPage": paginator.num_pages}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 文章阅读数排序
@csrf_exempt
def most_views(request):
    try:
        length = r.zcard('lightblog_ranking')
        article_ranking = r.zrange("lightblog_ranking", 0, length, desc=True)[:5]
        article_ranking_ids = [int(id) for id in article_ranking]
        most_viewed = list(LightBlogArticle.objects.filter(id__in=article_ranking_ids))
        most_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))
        articles = []
        for i in range(len(most_viewed)):
            view = r.get('lightblog:{}:views'.format(most_viewed[i].id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
            articles.append({"id": most_viewed[i].id,
                             "title": most_viewed[i].title,
                             "description": most_viewed[i].article_descripton,
                             "specialColumn": most_viewed[i].specialColumn.special_column,
                             "specialColumnId": most_viewed[i].specialColumn.id,
                             "specialTheme": most_viewed[i].specialTheme.special_theme,
                             "specialThemeId": most_viewed[i].specialTheme.id,
                             "created": time.mktime(most_viewed[i].created.timetuple()),
                             "updated": time.mktime(most_viewed[i].updated.timetuple()),
                             "checked": time.mktime(most_viewed[i].checkTime.timetuple()) if most_viewed[i].checkTime else '',
                             "usersLike": most_viewed[i].users_like.count(),
                             "usersDisLike": most_viewed[i].users_dislike.count(),
                             "scanCount": view_count,
                             "wordCount": most_viewed[i].article_wordCount,
                             "body": init_blog(most_viewed[i].article_body)[:100],
                             'blog_img_url': most_viewed[i].article_preview.url,
                             'author_img_url': most_viewed[i].author.userinfo.photo_150x150.url,
                             'author': most_viewed[i].author.username})
        return HttpResponse(
            json.dumps({"success": True, "data": articles}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))



# 返回专栏数据
@csrf_exempt
def get_special_column(request):
    try:
        specialColumnList = LightBlogSpecialColumn.objects.filter(Q(isPublish=1)&Q(isRecommend=True))
        list = []
        for i in range(len(specialColumnList)):
            list.append({
                "id": specialColumnList[i].id,
                "specialColumnName": specialColumnList[i].special_column,
                "description": specialColumnList[i].description,
                "image_preview": specialColumnList[i].image_preview.url
            })
        return HttpResponse(json.dumps({"success": True, "data": list}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))
