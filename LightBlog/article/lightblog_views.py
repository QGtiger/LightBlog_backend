from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost, LightBlogSpecialColumn,LightBlogSpecialTheme,LightBlogBanner, LightBlogArticle
from django.conf import settings
from .tasks import *
import json
import redis
import re
import time
import jwt
from .utils import get_user
from django.conf import settings
from .utils import is_superuser, log_in
from django.core import serializers
from .homePage import init_blog
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def nullParam():
    return ''

# 发布专栏
@csrf_exempt
def publish_special_column(request):
    try:
        columnId = request.POST.get('columnId', '')
        column = LightBlogSpecialColumn.objects.get(id=columnId)
        column.isPublish = 1
        column.save()
        return HttpResponse(json.dumps({"success": True, "tips": '发布成功'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 推荐专栏
@csrf_exempt
def recommend_special_column(request):
    try:
        type = request.POST.get('type', '')
        columnId = request.POST.get('columnId', '')
        column = LightBlogSpecialColumn.objects.get(id=columnId)
        if type == "notRecommend":
            column.isRecommend = False
            column.save()
            return HttpResponse(json.dumps({"success": True, "code": 200, "tips": "下架推荐成功"}))
        if LightBlogSpecialColumn.objects.filter(isRecommend=True).count() >= 3:
            return HttpResponse(json.dumps({"success": True, "code": 201, "tips": "推荐专栏不能多余三个"}))
        if column.isPublish == 0:
            return HttpResponse(json.dumps({"success": True, "code": 202, "tips": "请先发布该专栏再推荐"}))
        column.isRecommend = True
        column.save()
        return HttpResponse(json.dumps({"success":True,"code":200,"tips":"推荐成功"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 下架 专栏
@csrf_exempt
def down_special_column(request):
    try:
        columnId = request.POST.get('columnId', '')
        column = LightBlogSpecialColumn.objects.get(id=columnId)
        LightBlogSpecialColumn.objects.filter(id=columnId).update(isPublish=0, isRecommend=False)
        LightBlogSpecialTheme.objects.filter(special_column=column).update(isPublish=0)
        return HttpResponse(json.dumps({"success": True, 'tips': '下架成功'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))



# 返回专栏
@csrf_exempt
def special_column(request):
    try:
        columnList = LightBlogSpecialColumn.objects.all()
        status = request.POST.get('status', '')
        is_return_img = request.POST.get('is_img', '')
        if status != '':
            columnList = columnList.filter(isPublish=status)
        special_column_list = []
        for i in range(len(columnList)):
            special_column_list.append({"specialColumn": columnList[i].special_column,
                                        "id": columnList[i].id,
                                        'created': time.mktime(columnList[i].created.timetuple()),
                                        'description': columnList[i].description,
                                        "status": columnList[i].isPublish,
                                        "isRecommend": columnList[i].isRecommend,
                                        "preview": columnList[i].image_preview.url if is_return_img != '' else ''})
        return HttpResponse(json.dumps({"success": True, "data": special_column_list, "total":len(columnList)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 上传专栏
@csrf_exempt
def add_special_column(request):
    try:
        column_name = request.POST.get('columnName','')
        description = request.POST.get('description', '')
        cover_image = request.FILES.get('cover_image', '')
        if column_name == '' or description == '':
            return HttpResponse(json.dumps({"success": False, "tips": "不能为空"}))
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        column = LightBlogSpecialColumn(create_user=user, special_column=column_name, description=description)
        column.save()
        column.image_preview.save(str(column.special_column) + '.jpg', cover_image)
        return HttpResponse(json.dumps({"success": True, "tips": '专栏创建成功'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": 'somethong error'}))


@csrf_exempt
def del_special_column(request):
    try:
        column_id = request.POST.get('columnId', '')
        column = LightBlogSpecialColumn.objects.get(id=column_id)
        column.delete()
        return HttpResponse(json.dumps({"success": True, "tips": '专栏删除成功'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": 'somethong error'}))


@csrf_exempt
def special_column_detail(request):
    try:
        column_id = request.POST.get('columnId', '')
        column = LightBlogSpecialColumn.objects.get(id=column_id)
        column_detail = {
            "description": column.description,
            "created": time.mktime(column.created.timetuple()),
            "special_column": column.special_column,
            "createUser": column.create_user.username,
            "previewImg": column.image_preview.url
        }
        return HttpResponse(json.dumps({"success": True, "data": column_detail}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 更新update专栏
@csrf_exempt
def update_special_column(request):
    try:
        column_id = request.POST.get('columnId', '')
        description = request.POST.get('description', '')
        column_name = request.POST.get('columnName', '')
        is_updateImage = request.POST.get('isUpdateImage', '')
        column = LightBlogSpecialColumn.objects.get(id=column_id)
        column.special_column = column_name
        column.description = description
        column.save()
        if is_updateImage == '1':
            cover_image = request.FILES.get('cover_image', '')
            column.image_preview.save(str(column.special_column) + '.jpg', cover_image)
        return HttpResponse(json.dumps({"success": True, "tips": "修改成功"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def init_data(data):
    list = []
    for item in data:
        list.append({
            "id": item.id,
            "title": item.title
        })
    return list

# 获取专题list
@csrf_exempt
def special_theme(request):
    try:
        page = request.GET.get('page')
        size = request.GET.get('size',1000)
        status = request.POST.get('status', '')
        columnId = request.POST.get('columnId', '')
        content = request.POST.get('content', '')
        themeList = LightBlogSpecialTheme.objects.all()
        is_return_img = request.POST.get('is_img', '') # 返回图片路径相当于在专题页面下
        column = None
        if columnId != '':
            column = LightBlogSpecialColumn.objects.get(id=columnId)
            themeList = themeList.filter(special_column=column)
        if content != '':
            themeList = themeList.filter(special_theme__icontains=content)
        if status != '':
            themeList = themeList.filter(isPublish=status)
        paginator = Paginator(themeList, size)
        try:
            current_page = paginator.page(page)
            list = current_page.object_list
        except PageNotAnInteger:
            current_page = paginator.page(1)
            list = current_page.object_list
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)
            list = current_page.object_list
        special_theme_list = []
        for item in list:
            blogList = LightBlogArticle.objects.filter(isRecommend=True).filter(specialTheme=item)[:3]
            special_theme_list.append({"specialColumn": item.special_column.special_column,
                                       "specialColumnId":item.special_column.id,
                                       "specialThemeId": item.id,
                                       "specialTheme": item.special_theme,
                                       'created': time.mktime(item.created.timetuple()),
                                       'description': item.description,
                                       "status": item.isPublish,
                                       "preview": item.image_preview.url if is_return_img != '' else '',
                                       "recommendBlogs": init_data(blogList) if is_return_img != '' else ''})
        return HttpResponse(json.dumps({"success": True, "data": special_theme_list, "total":len(themeList), "columnName": column.special_column if column else '全部', "columnDesc": column.description if column else "LightBlog's column of all."}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 新增专题
@csrf_exempt
def add_special_theme(request):
    try:
        themeName = request.POST.get('themeName','')
        columnId = request.POST.get('columnId', '')
        description = request.POST.get('description', '')
        cover_image = request.FILES.get('cover_image', '')
        if themeName == '' or description == '':
            return HttpResponse(json.dumps({"success": False, "tips": "不能为空"}))
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        column = LightBlogSpecialColumn.objects.get(id=columnId)
        theme = LightBlogSpecialTheme(create_user=user, special_column=column, description=description,special_theme=themeName)
        theme.save()
        theme.image_preview.save(str(theme.special_theme) + '.jpg', cover_image)
        return HttpResponse(json.dumps({"success": True, "tips": '专题创建成功'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 删除专题
@csrf_exempt
def del_special_theme(request):
    try:
        themeId = request.POST.get('themeId', '')
        theme = LightBlogSpecialTheme.objects.get(id=themeId)
        theme.delete()
        return HttpResponse(json.dumps({"success": True, "tips": "删除专题成功"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 专题详情
@csrf_exempt
def detail_special_theme(request):
    try:
        themeId = request.POST.get('themeId', '')
        theme = LightBlogSpecialTheme.objects.get(id=themeId)
        theme_detail = {
            "description": theme.description,
            "created": time.mktime(theme.created.timetuple()),
            "special_columnId": theme.special_column.id,
            "createUser": theme.create_user.username,
            "previewImg": theme.image_preview.url,
            "special_theme": theme.special_theme
        }
        return HttpResponse(json.dumps({"success": True, "data": theme_detail}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 更新update 专题
@csrf_exempt
def update_special_theme(request):
    try:
        themeId = request.POST.get('themeId', '')
        description = request.POST.get('description', '')
        themeName = request.POST.get('themeName', '')
        columnId = request.POST.get('columnId', '')
        is_updateImage = request.POST.get('isUpdateImage', '')
        theme = LightBlogSpecialTheme.objects.get(id=themeId)
        theme.special_theme = themeName
        theme.description = description
        if theme.special_column.id != columnId:
            column = LightBlogSpecialColumn.objects.get(id=columnId)
            theme.special_column = column
        theme.save()
        if is_updateImage == '1':
            cover_image = request.FILES.get('cover_image', '')
            theme.image_preview.save(str(theme.special_theme) + '.jpg', cover_image)
        return HttpResponse(json.dumps({"success": True, "tips": "修改成功"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 发布专题
@csrf_exempt
def publish_special_theme(request):
    try:
        themeId = request.POST.get('themeId', '')
        theme = LightBlogSpecialTheme.objects.get(id=themeId)
        if theme.special_column.isPublish == 0:
            return HttpResponse(json.dumps({"success": True, "code": 201, "tips": "该专题所属专栏未发布，不能发布该专题"}))
        LightBlogSpecialTheme.objects.filter(id=themeId).update(isPublish=1)

        return HttpResponse(json.dumps({"success": True, "code":200,"tips": "发布成功"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 下架专题
@csrf_exempt
def down_special_theme(request):
    try:
        themeId = request.POST.get('themeId', '')
        LightBlogSpecialTheme.objects.filter(id=themeId).update(isPublish=0)
        return HttpResponse(json.dumps({"success": True, "tips": "下架成功"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# banner 新增
@csrf_exempt
def add_banner(request):
    try:
        title = request.POST.get('title', nullParam())
        desc = request.POST.get('desc', nullParam())
        url = request.POST.get('url', nullParam())
        image = request.FILES.get('image', nullParam())
        banner = LightBlogBanner()
        banner.title = title
        banner.desc = desc
        banner.url = url
        banner.save()
        banner.image.save(title+'.jpg', image)
        return HttpResponse(json.dumps({"success": True, "tips":"ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# banner 修改
@is_superuser
def update_banner(request):
    try:
        id = request.POST.get('id', nullParam())
        title = request.POST.get('title', nullParam())
        desc = request.POST.get('desc', nullParam())
        url = request.POST.get('url', nullParam())
        LightBlogBanner.objects.filter(id=id).update(title=title, desc=desc, url=url)
        isUpdateImg = request.POST.get('isUpdateImg', False)
        if isUpdateImg == 'true':
            image = request.FILES.get('image', nullParam())
            banner = LightBlogBanner.objects.get(id=id)
            banner.image.save(title+'.jpg', image)
        return HttpResponse(json.dumps({"success": True, "tips":"ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))

# 获取banner list信息
def get_banner(request):
    try:
        banners = LightBlogBanner.objects.all()
        list = []
        for i in range(len(banners)):
            list.append({
                'id': banners[i].id,
                'title': banners[i].title,
                'desc': banners[i].desc,
                'url': banners[i].url,
                'image': banners[i].image.url
            })
        return HttpResponse(json.dumps({"success": True, "list": list}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": True, "tips": str(e)}))


def banner_detail(request):
    try:
        id = request.POST.get('id', nullParam())
        banner = LightBlogBanner.objects.get(id=id)
        detail = {
            "id": id,
            "title": banner.title,
            "desc": banner.desc,
            "url": banner.url,
            "image": banner.image.url
        }
        return HttpResponse(json.dumps({"success": True, "data": detail}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


@is_superuser
def del_banner(request):
    try:
        id = request.POST.get('id', '')
        banner = LightBlogBanner.objects.get(id=id)
        banner.delete()
        return HttpResponse(json.dumps({"success": True, "tips": "ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def theme_blog(request):
    try:
        themeId = request.POST.get('themeId', '')
        theme = LightBlogSpecialTheme.objects.get(id=themeId)
        themeBlog_all = theme.article_specialtheme.all()
        size = request.GET.get('size',10)
        paginator = Paginator(themeBlog_all, size)
        page = request.GET.get('page','')
        try:
            current_page = paginator.page(page)
            blogs = current_page.object_list
        except PageNotAnInteger:
            current_page = paginator.page(1)
            blogs = current_page.object_list
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)
            blogs = current_page.object_list
        list_blog = []
        for item in blogs:
            view = r.get('lightblog:{}:views'.format(item.id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
            list_blog.append({"id": item.id,
                             "title": item.title,
                             "description": item.article_descripton,
                             "specialColumn": item.specialColumn.special_column,
                             "specialColumnId": item.specialColumn.id,
                             "specialTheme": item.specialTheme.special_theme,
                             "specialThemeId": item.specialTheme.id,
                             "personalColumn": item.personalColumn.personal_column,
                             "created": time.mktime(item.created.timetuple()),
                             "updated": time.mktime(item.updated.timetuple()),
                             "checked": time.mktime(item.checkTime.timetuple()) if item.checkTime else '',
                             "usersLike": item.users_like.count(),
                             "usersDisLike": item.users_dislike.count(),
                             "scanCount": view_count,
                             "wordCount": item.article_wordCount,
                             "body": init_blog(item.body_html)[:200],
                             'blog_img_url': item.article_preview.url,
                             'author_img_url': item.author.userinfo.photo_150x150.url,
                             'author': item.author.username})
        return HttpResponse(json.dumps({"success": True, "data": list_blog, "themeName": theme.special_theme, "total": theme.article_specialtheme.count()}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def lightblog_like(request):
    user = get_user(request)
    article_id = request.POST.get('id', '')
    action = request.POST.get('action', '')
    try:
        article = LightBlogArticle.objects.get(id=article_id)
        if action == 'like':
            likeCount = article.users_like.all()
            is_liked = user in likeCount
            if is_liked:
                article.users_like.remove(user)
                return HttpResponse(json.dumps({"success": True, 'tips': '回收自己的点赞',"is_like": False ,'like_count': article.users_like.count()}))
            else:
                article.users_like.add(user)
                return HttpResponse(json.dumps({"success": True, 'tips': '感谢你的点赞',"is_like": True ,"like_count": article.users_like.count()}))
        else:
            dislikeAll = article.users_dislike.all()
            is_dislike = user in dislikeAll
            if is_dislike:
                article.users_dislike.remove(user)
                return HttpResponse(json.dumps({"success": True, "tips": '回收 踩一下',"is_dislike": False, 'dislike_count': article.users_dislike.count()}))
            else:
                article.users_dislike.add(user)
                return HttpResponse(json.dumps({"success": True, "tips": '踩一下',"is_dislike": True ,"dislike_count": article.users_dislike.count()}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def lightblog_collection(request):
    user = get_user(request)
    article_id = request.POST.get('id', '')
    action = request.POST.get('action', '')
    try:
        article = LightBlogArticle.objects.get(id=article_id)
        collectionAll = article.collector.all()
        is_collection = user in collectionAll
        if action == 'collect':
            if is_collection:
                return HttpResponse(json.dumps({"success": False, "tips":'您已经收藏了改文章'}))
            else:
                article.collector.add(user)
                return HttpResponse(json.dumps({"success": True, "tips": "感谢您的收藏"}))
        else:
            if is_collection:
                article.collector.remove(user)
                return HttpResponse(json.dumps({"success": True, "tips": "已经成功 移出 您的收藏夹"}))
            else:
                return HttpResponse(json.dumps({"success": False, "tips": "您未收藏改文章"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def myself_collect_blog(request):
    try:
        user = get_user(request)
        article_list = user.lightblog_collector.all()
        responseData = []
        for item in article_list:
            view = r.get('lightblog:{}:views'.format(item.id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
            responseData.append({"id": item.id,
                             "title": item.title,
                             "description": item.article_descripton,
                             "specialColumn": item.specialColumn.special_column,
                             "specialColumnId": item.specialColumn.id,
                             "specialTheme": item.specialTheme.special_theme,
                             "specialThemeId": item.specialTheme.id,
                             "personalColumn": item.personalColumn.personal_column,
                             "created": time.mktime(item.created.timetuple()),
                             "updated": time.mktime(item.updated.timetuple()),
                             "isRecommend": item.isRecommend,
                             "usersLike": item.users_like.count(),
                             "usersDisLike": item.users_dislike.count(),
                             "scanCount": view_count,
                             "author": item.author.username,
                             "status": item.article_status,
                             "wordCount": item.article_wordCount,
                                "articlePreview": item.article_preview.url})
            # responseData.append({
            #     "title": item.title,
            #     "id": item.id,
            #     "author": item.author.username,
            #     "special_column": item.specialColumn.special_column,
            #     "special_column_id": item.specialColumn.id,
            #     "special_theme": item.specialTheme.special_theme,
            #     "special_theme_id": item.specialTheme.id,
            # })
        return HttpResponse(json.dumps({"success": True, "data": responseData, "tips": 'OK'}))
    except Exception as e:
        return  HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def remove_favorites(request):
    try:
        user = get_user(request)
        id = request.POST.get('id','')
        article = LightBlogArticle.objects.get(id=id)
        favorites_list = user.lightblog_collector.all()
        is_collected = article in favorites_list
        if is_collected:
            article.collector.remove(user)
            return HttpResponse(json.dumps({"success": True,"tips": "已成功移出您次收藏夹"}))
        else:
            return HttpResponse(json.dumps({"success": False,"tips": "您未收藏改文章"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))
