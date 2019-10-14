from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost, Comment,LightBlogSpecialColumn
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


# 返回专栏
def special_column(request):
    try:
        list = LightBlogSpecialColumn.objects.all()
        special_column_list = []
        for i in range(len(list)):
            special_column_list.append({"specialColumn": list[i].special_column, "id": list[i].id, 'created': time.mktime(list[i].created.timetuple()),'description': list[i].description})
        return HttpResponse(json.dumps({"success": True, "data": special_column_list, "total":len(list)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": 'somethong error'}))


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