from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost, Comment,LightBlogSpecialColumn,LightBlogSpecialTheme
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


# 下架 专栏
@csrf_exempt
def down_special_column(request):
    try:
        columnId = request.POST.get('columnId', '')
        column = LightBlogSpecialColumn.objects.get(id=columnId)
        LightBlogSpecialColumn.objects.filter(id=columnId).update(isPublish=0)
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
        if status != '':
            columnList = columnList.filter(isPublish=status)
        special_column_list = []
        for i in range(len(columnList)):
            special_column_list.append({"specialColumn": columnList[i].special_column,
                                        "id": columnList[i].id,
                                        'created': time.mktime(columnList[i].created.timetuple()),
                                        'description': columnList[i].description,
                                        "status": columnList[i].isPublish})
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


# 获取专题list
@csrf_exempt
def special_theme(request):
    try:
        page = request.GET.get('page')
        size = request.GET.get('size')
        status = request.POST.get('status', '')
        columnId = request.POST.get('columnId', '')
        content = request.POST.get('content', '')
        themeList = LightBlogSpecialTheme.objects.all()
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
        for i in range(len(list)):
            special_theme_list.append({"specialColumn": list[i].special_column.special_column,
                                       "specialColumnId":list[i].special_column.id,
                                       "specialThemeId": list[i].id,
                                       "specialTheme": list[i].special_theme,
                                       'created': time.mktime(list[i].created.timetuple()),
                                       'description': list[i].description,
                                       "status": list[i].isPublish})
        return HttpResponse(json.dumps({"success": True, "data": special_theme_list, "total":len(themeList)}))
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
        LightBlogSpecialTheme.objects.filter(id=themeId).update(isPublish=1)
        return HttpResponse(json.dumps({"success": True, "tips": "发布成功"}))
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