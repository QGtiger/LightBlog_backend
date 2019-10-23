from django.shortcuts import get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import LightBlogReplyTemplate
from .tasks import *
import json
import jwt
from django.conf import settings
import datetime

#验证是否是superuser
def isSuperUser(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    user = User.objects.get(username=username)
    if not user.is_superuser:
        return HttpResponse(json.dumps({"success": False, 'tips': "您没有权限"}))

def nullParam():
    return HttpResponse(json.dumps({"success": False, 'tips': "参数不能为空"}))

# 新增模板
@csrf_exempt
def add_template(request):
    try:
        isSuperUser(request)
        title = request.POST.get('title', nullParam())
        content = request.POST.get('content', nullParam())
        template = LightBlogReplyTemplate(title=title, content=content)
        template.save()
        return HttpResponse(json.dumps({"success": True, "tips": 'ok'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


@csrf_exempt
def get_template(request):
    try:
        isSuperUser(request)
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 1000)
        templateListAll = LightBlogReplyTemplate.objects.all()
        paginator = Paginator(templateListAll, size)
        try:
            current_page = paginator.page(page)
            list = current_page.object_list
        except PageNotAnInteger:
            current_page = paginator.page(1)
            list = current_page.object_list
        except EmptyPage:
            current_page = paginator.page(paginator.num_pages)
            list = current_page.object_list
        templates = []
        for i in range(len(list)):
            templates.append({
                "id": list[i].id,
                "title": list[i].title,
                "content": list[i].content
            })
        return HttpResponse(json.dumps({"success": True, "data": templates, "total": len(templateListAll)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success":False, "tips": str(e)}))


@csrf_exempt
def detail_template(request):
    try:
        isSuperUser(request)
        id = request.POST.get('id', nullParam())
        template = LightBlogReplyTemplate.objects.get(id=id)
        return HttpResponse(json.dumps({"success": True, "data": {
            "id": id,
            "title": template.title,
            "content": template.content
        }}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


@csrf_exempt
def update_template(requset):
    try:
        isSuperUser(requset)
        id = requset.POST.get('id', nullParam())
        title = requset.POST.get('title', nullParam())
        content = requset.POST.get('content', nullParam())
        LightBlogReplyTemplate.objects.filter(id=id).update(title=title,content=content)
        return HttpResponse(json.dumps({"success": True, "tips": "ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


@csrf_exempt
def del_template(request):
    try:
        isSuperUser(request)
        id = request.POST.get('id', nullParam())
        template = LightBlogReplyTemplate.objects.get(id=id)
        template.delete()
        return HttpResponse(json.dumps({"success": True, "tips": "ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))