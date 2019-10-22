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

# 获取用户   token = request.META.get('HTTP_AUTHORIZATION')
def getUser(token):
    dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    user = User.objects.get(username=username)
    return user


# 验证修饰符
def checkUser(func):
    def check(request):
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        id = request.POST.get(id, '')
        article = LightBlogArticle.objects.get(id=id)
        if user != article.author:
            return HttpResponse(json.dumps({"success":False,"tips":"您并没有权限"}))
        else:
            return func(request)
    return check


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
            view = r.get('lightblog:{}:views'.format(list[i].id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
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
                             "scanCount": view_count,
                                "status": list[i].article_status})
        return HttpResponse(json.dumps({"success": True, "data": articles, "total": len(articleList)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))


# 发布文章时的获取column和theme
@csrf_exempt
def get_column_theme(request):
    try:
        columnList = LightBlogSpecialColumn.objects.filter(isPublish=1)
        columnData = []
        themeData = {}
        for i in range(len(columnList)):
            columnData.append({
                "id": columnList[i].id,
                "columnName": columnList[i].special_column,
                'description': columnList[i].description
            })
            themeList = columnList[i].lightblog_specialcolumn.all().filter(isPublish=1)
            data = []
            for i in range(len(themeList)):
                data.append({
                    "id": themeList[i].id,
                    "themeName": themeList[i].special_theme
                })
            themeData[columnList[i].id] = data
        return HttpResponse(json.dumps({"success": True, "data": {"columnList": columnData, "themeList": themeData}}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 发布文章
@csrf_exempt
def publish_article(request):
    try:
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        specialColumnId = request.POST.get('specialColumnId', '')
        specialThemeId = request.POST.get('specialThemeId', '')
        personalColumnId = request.POST.get('personalColumnId', '')
        isUpdateImg = request.POST.get('isUpdateImg', '')
        # print(title,description,specialColumnId,isUpdateImg)
        specialColumn = LightBlogSpecialColumn.objects.get(id=specialColumnId)
        specialTheme = LightBlogSpecialTheme.objects.get(id=specialThemeId)
        personalColumn = LightBlogPersonalColumn.objects.get(id=personalColumnId)
        token = request.META.get('HTTP_AUTHORIZATION')
        user = getUser(token)
        article = LightBlogArticle(author=user,title=title,article_descripton=description,specialColumn=specialColumn,specialTheme=specialTheme,personalColumn=personalColumn)
        article.save()
        if isUpdateImg == '1':
            previewImg = request.FILES.get('previewImg', '')
            article.article_preview.save(str(article.title) + '.jpg', previewImg)
        return HttpResponse(json.dumps({"success": True, 'tips':'发布成功', 'data': {"id": article.id}}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


#文章更新
@csrf_exempt
def update_article(request):
    try:
        id = request.POST.get('id', '')
        article = LightBlogArticle.objects.get(id=id)
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        if username != article.author.username:
            return HttpResponse(json.dumps({"success": False, "tips": '您并没有权限修改该文章'}))
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        specialColumnId = request.POST.get('specialColumnId', '')
        specialThemeId = request.POST.get('specialThemeId', '')
        personalColumnId = request.POST.get('personalColumnId', '')
        body = request.POST.get('body', '')
        bodyHtml = request.POST.get('body_html', '')
        isUpdateImg = request.POST.get('isUpdateImg', '')
        specialColumn = LightBlogSpecialColumn.objects.get(id=specialColumnId)
        specialTheme = LightBlogSpecialTheme.objects.get(id=specialThemeId)
        personalColumn = LightBlogPersonalColumn.objects.get(id=personalColumnId)
        LightBlogArticle.objects.filter(id=id).update(title=title,article_descripton=description,specialColumn=specialColumn,specialTheme=specialTheme,personalColumn=personalColumn,article_body=body,body_html=bodyHtml)
        if isUpdateImg == '1':
            previewImg = request.FILES.get('previewImg', '')
            article.article_preview.save(str(article.title) + '.jpg', previewImg)
        return HttpResponse(json.dumps({"success": True, 'tips': '修改成功'}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))



# 文章编辑
@csrf_exempt
def detail_article(request):
    try:
        id = request.POST.get('id', '')
        article = LightBlogArticle.objects.get(id=id)
        detailArticle = {
            "title": article.title,
            "description": article.article_descripton,
            "previewImg": [{"url":article.article_preview.url}],
            "columnId": article.specialColumn.id,
            "columnName": article.specialColumn.special_column,
            "themeId": article.specialTheme.id,
            "themeName": article.specialTheme.special_theme,
            "personalColumnId": article.personalColumn.id,
            "body": article.article_body,
            "bodyHtml": article.body_html
        }
        return HttpResponse(json.dumps({"success": True, "data": detailArticle, "tips": "OK"}))
    except Exception as e:
        return  HttpResponse(json.dumps({"success": False, "tips": str(e)}))


# 文章删除
@csrf_exempt
def del_article(request):
    try:
        id=request.POST.get("id", '')
        article = LightBlogArticle.objects.get(id=id)
        article.delete()
        return HttpResponse(json.dumps({"success": True, "tips":"ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))



from PIL import Image

# 文章图片上传
@csrf_exempt
def upload_articleImg(request):
    try:
        id = request.POST.get('id', '')
        uploadImage = request.FILES.get('image', '')
        uploadImageName = request.POST.get('imageName', '')
        article = LightBlogArticle.objects.get(id=id)
        articleImg = LightBlogArticleImage(article=article)
        articleImg.image.save(uploadImageName, uploadImage)
        # imgPath = os.path.join(settings.BASE_DIR,'media','\\'.join(str(articleImg.image).split('/')))
        # print(imgPath)
        image = Image.open(uploadImage)
        width = image.width
        height = image.height
        rate = 1.0 # 压缩率
        # 根据图像大小设置压缩率
        if width >= 2000 or height >= 2000:
            rate = 0.3
        elif width >= 1000 or height >= 1000:
            rate = 0.5
        elif width >= 500 or height >= 500:
            rate = 0.7
        width = int(width * rate)  # 新的宽
        height = int(height * rate)  # 新的高
        image.thumbnail((width, height), Image.ANTIALIAS)  # 生成缩略图
        if not os.path.exists(settings.MEDIA_ROOT+'/LightBlogArticleImagesCompress/'+id):
            os.mkdir(settings.MEDIA_ROOT+'/LightBlogArticleImagesCompress/'+id)
        image.save(settings.MEDIA_ROOT+'/LightBlogArticleImagesCompress/'+id+ '/'+str(uploadImageName), 'JPEG')
        articleImg.imageCompress = 'LightBlogArticleImagesCompress/'+id+ '/'+str(uploadImageName)
        articleImg.save()
        return HttpResponse(json.dumps({"success": True, 'tips': "ok", "data":{"image": articleImg.image.url, "imageCompress": articleImg.imageCompress.url}}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))


# 文章申请发布
@csrf_exempt
def applyShowArticle(request):
    try:
        id = request.POST.get('id','')
        article = LightBlogArticle.objects.get(id=id)
        article.article_status = 1
        article.save()
        return HttpResponse(json.dumps({"success": True, "tips": "ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))


# admin文章获取
@csrf_exempt
def get_all_article(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        user = getUser(token)
        if user.is_superuser:
            articleList = LightBlogArticle.objects.exclude(article_status=0)
        else:
            return HttpResponse(json.dumps({"success": False, "tips":"您没有权限"}))
        status = request.POST.get('status', '')
        columnId = request.POST.get('columnId', '')
        themeId = request.POST.get('themeId', '')
        dateStart = request.POST.get('dateStart', '')
        queryKey = request.POST.get('queryKey', '')
        if status != '':
            articleList = articleList.filter(article_status=status)
        if columnId != '':
            specialColumn = LightBlogSpecialColumn.objects.get(id=columnId)
            articleList = articleList.filter(specialColumn=specialColumn)
        if themeId != '':
            specialTheme = LightBlogSpecialTheme.objects.get(id=themeId)
            articleList = articleList.filter(specialTheme=specialTheme)
        if dateStart != '':
            start = datetime.datetime.strptime(dateStart, '%Y-%m-%d %H:%M:%S')
            articleList = articleList.filter(updated__gt=start)
        if queryKey != '':
            articleList = articleList.filter(title__icontains=queryKey)
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
            view = r.get('lightblog:{}:views'.format(list[i].id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
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
                             "scanCount": view_count,
                             "author": list[i].author.username,
                                "status": list[i].article_status})
        return HttpResponse(json.dumps({"success": True, "data": articles, "total": len(articleList)}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, 'tips': str(e)}))