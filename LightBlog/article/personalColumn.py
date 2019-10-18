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


# 获取个人专栏的LIST
@csrf_exempt
def get_column(request):
    try:
        page = request.GET.get('page', '')
        size = request.GET.get('size', '')
        status = request.POST.get('status', '')
        content = request.POST.get('columnName', '')
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        columnList = LightBlogPersonalColumn.objects.filter(create_user=user)
        if len(columnList) == 0:
            return HttpResponse(json.dumps({"success": True, "total": len(columnList)}))
        if status != '':
            columnList = columnList.filter(status=status)
        if content != '':
            columnList = columnList.filter(personal_column__icontains=content)
        if size == '':
            size = 100
        paginator = Paginator(columnList, size)
        try:
            current_page = paginator.page(page)
            list = current_page.object_list
        except PageNotAnInteger:
            current_page = paginator.page(1)
            list = current_page.object_list
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)
            list = current_page.object_list
        column_list = []
        for i in range(len(list)):
            column_list.append({"columnName": list[i].personal_column,
                                "id": list[i].id,
                                "description": list[i].description,
                                "created": time.mktime(list[i].created.timetuple()),
                                "status": list[i].status})
        return  HttpResponse(json.dumps({"success": True, "data": column_list, "total": len(columnList)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))


# 新增个人专栏
@csrf_exempt
def add_column(request):
    try:
        columnName = request.POST.get('columnName', '')
        description = request.POST.get('description', '')
        cover_image = request.FILES.get('cover_image', '')
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        column = LightBlogPersonalColumn(create_user=user,personal_column=columnName,description=description)
        column.save()
        column.image_preview.save(str(column.personal_column) + '.jpg', cover_image)
        return HttpResponse(json.dumps({"success": True, 'tips': "ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 个人专栏详情
@csrf_exempt
def column_detail(request):
    try:
        columnId = request.POST.get('columnId', '')
        column = LightBlogPersonalColumn.objects.get(id=columnId)
        column_detail = {
            "description": column.description,
            "created": time.mktime(column.created.timetuple()),
            "columnName": column.personal_column,
            "createUser": column.create_user.username,
            "previewImg": column.image_preview.url
        }
        return HttpResponse(json.dumps({"success": True, "data": column_detail}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 更新个人专栏
@csrf_exempt
def update_column(request):
    try:
        columnId = request.POST.get('columnId', '')
        description = request.POST.get('description', '')
        columnName = request.POST.get('columnName', '')
        isUpdateImage = request.POST.get('isUpdateImage', '')
        LightBlogPersonalColumn.objects.filter(id=columnId).update(personal_column=columnName,description=description)
        if isUpdateImage == '1':
            cover_image = request.FILES.get('cover_image', '')
            column = LightBlogPersonalColumn.objects.get(id=columnId)
            column.image_preview.save(str(column.personal_column) + '.jpg', cover_image)
        return HttpResponse(json.dumps({"success": True, "tips": "修改成功"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success":False, "tips": str(e)}))


# 删除个人专栏
@csrf_exempt
def del_column(request):
    try:
        columnId = request.POST.get('columnId', '')
        column = LightBlogPersonalColumn.objects.get(id=columnId)
        column.delete()
        return HttpResponse(json.dumps({"success": True, "tips": '删除成功'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))
