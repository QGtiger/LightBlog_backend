from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import random
from django.contrib.auth.hashers import make_password
import re
from django.views.decorators.http import require_POST
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from .models import UserInfo,UserToken
from django.contrib.auth.decorators import login_required
from article.models import ArticlePost,LightBlogSpecialColumn,LightBlogSpecialTheme,LightBlogPersonalColumn,LightBlogArticle, LightBlogArticleImage
from article.list_views import init_blog
from .forms import *
import json
import time
import os
import redis
import jwt
from django.conf import settings
from datetime import datetime, timedelta
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

# 获取用户   token = request.META.get('HTTP_AUTHORIZATION')
def getUser(token):
    dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    user = User.objects.get(username=username)
    return user


def nullParam():
    return HttpResponse(json.dumps({"success": False, 'tips': "参数不能为空"}))

# 上传头像
@csrf_exempt
def upload_avator(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        uploadImg = request.FILES.get('uploadimg', nullParam())
        user = User.objects.get(username=username)
        userinfo = UserInfo.objects.get(user=user)
        userinfo.photo.save(username + '.jpg', uploadImg)
        return HttpResponse(json.dumps({"success": True, "tips": "上传成功", "avator": userinfo.photo.url}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 上传头像
@csrf_exempt
def upload_author_background(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        uploadImg = request.FILES.get('uploadimg', nullParam())
        user = User.objects.get(username=username)
        userinfo = UserInfo.objects.get(user=user)
        userinfo.user_bg.save(username + '-bg.jpg', uploadImg)
        return HttpResponse(json.dumps({"success": True, "tips": "上传成功", "author_bg": userinfo.user_bg.url}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 获取用户信息
@csrf_exempt
def detail_author(request):
    try:
        username = request.POST.get('username', nullParam())
        if username == '':
            token = request.META.get('HTTP_AUTHORIZATION')
            dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        userinfo = UserInfo.objects.get(user=user)
        userDetail = {
            "username": username,
            "avatorUrl": userinfo.photo.url,
            "recommendBlogs": user.lightblog_article.filter(isRecommend=True).count(),
            "publishBlogs": user.lightblog_article.count(),
            "authorBg": userinfo.user_bg.url
        }
        recommendBlogs = user.lightblog_article.filter(isRecommend=True)
        recommendBlogList = []

        return HttpResponse(json.dumps({"success": True, "userDetail": userDetail}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 获取用户文章，推荐发布，点赞等
@csrf_exempt
def get_author_blog(request):
    try:
        username = request.POST.get('username', nullParam())
        if username == '':
            token = request.META.get('HTTP_AUTHORIZATION')
            dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            username = dict.get('data').get('username')
        blog_type = request.POST.get('blogtype', nullParam())
        page = request.POST.get('page', 1)
        size = request.POST.get('size', 10)
        user = User.objects.get(username=username)
        if blog_type == 'recommend':
            blogs = user.lightblog_article.filter(isRecommend=True)
        elif blog_type == 'publish':
            blogs = user.lightblog_article.all()
        elif blog_type == 'like':
            blogs = user.lightblog_users_like.all()
        paginator = Paginator(blogs, size)
        try:
            current_page = paginator.page(page)
            list = current_page.object_list
        except PageNotAnInteger:
            current_page = paginator.page(1)
            list = current_page.object_list
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)
            list = current_page.object_list
        blog_list = []
        for i in range(len(list)):
            view = r.get('lightblog:{}:views'.format(list[i].id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
            blog_list.append({"id": list[i].id,
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
        return HttpResponse(json.dumps({"success": True, "blogList": blog_list, "totalpage": paginator.num_pages}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))



# 关注用户
def follow_author(request):
    try:
        follow_username = request.POST.get('follow', '')
        type = request.POST.get('type', '')
        user = User.objects.get(username=follow_username)
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        current_user = User.objects.get(username=username)
        if type == 'follow':
            followed_users = current_user.userinfo.user_follow.all()
            for item in followed_users:
                if item == user:
                    return HttpResponse(json.dumps({"success": False, "tips": "您已关注该博主"}))
            current_user.userinfo.user_follow.add(user)
            num = current_user.userinfo.user_follow.count()
            return HttpResponse(json.dumps({"success": True, "tips": "ok", "follow_count": num}))
        else:
            current_user.userinfo.user_follow.remove(user)
            num = current_user.userinfo.user_follow.count()
            return HttpResponse(json.dumps({"success": True, "tips": "ok", "follow_count": num}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# ta 关注的人
def follow_list(request):
    try:
        username = request.POST.get('username', '')
        current_user = User.objects.get(username=username)
        type = request.POST.get('type', '')
        page = request.POST.get('page', 1)
        size = request.POST.get('size', 10)
        if type == 'follow':
            follow_author_list = current_user.userinfo.user_follow.all()
            paginator = Paginator(follow_author_list, size)
            try:
                current_page = paginator.page(page)
                list = current_page.object_list
            except PageNotAnInteger:
                current_page = paginator.page(1)
                list = current_page.object_list
            except EmptyPage:
                current_page = paginator.page(paginator.num_pages)
                list = current_page.object_list

            user_list = []
            for item in list:
                user_list.append({
                    "id": item.id,
                    "username": item.username,
                    "aboutme": item.userinfo.aboutme,
                    "url": item.userinfo.photo_100x100.url
                })
        else:
            follow_author_list = current_user.user_follow.all()
            paginator = Paginator(follow_author_list, size)
            try:
                current_page = paginator.page(page)
                list = current_page.object_list
            except PageNotAnInteger:
                current_page = paginator.page(1)
                list = current_page.object_list
            except EmptyPage:
                current_page = paginator.page(paginator.num_pages)
                list = current_page.object_list
            user_list = []
            for item in list:
                user_list.append({
                    "id": item.user.id,
                    "username": item.user.username,
                    "aboutme": item.aboutme,
                    "url": item.photo_100x100.url
                })
        return HttpResponse(json.dumps({"success": True, "data": user_list, "total": len(follow_author_list)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))