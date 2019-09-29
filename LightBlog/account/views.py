from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import random
from django.contrib.auth.hashers import make_password
import re
from django.views.decorators.http import require_POST
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from .models import UserInfo,UserToken
from django.contrib.auth.decorators import login_required
from article.models import ArticlePost
from article.list_views import init_blog
from .forms import *
import json
import time
import os
import redis
import jwt
from datetime import datetime, timedelta
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


# Create your views here.
@csrf_exempt
def account_login(request):
    title = ' LFBlog 登录 '
    unit_2 = '/account/register/'
    unit_2_name = ' 立即注册 '
    unit_1 = '/account/setpassword/'
    unit_1_name = ' 修改密码 '
    if request.method == 'POST':
        username = request.POST.get('username', '')
        print(username)
        password = request.POST.get('password', '')
        if User.objects.filter(username=username):
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    # request.session['username'] = username #
                    # 验证是否登录成功，存储到session

                    # token
                    token = jwt.encode({
                            'exp':datetime.utcnow()+timedelta(seconds=settings.TOKEN_EXPIRE_TIME),
                            'iat':datetime.utcnow(),
                            'data': {
                                'username': username
                            }
                        },settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                    UserToken.objects.update_or_create(user=user, defaults={"token": token})
                    return HttpResponse(json.dumps(
                        {'status': 1, 'tips': ' 登录成功 ', 'token': token}))
            else:
                # tips = ' 账号错误，请重新输入 '
                return HttpResponse(json.dumps(
                    {'status': 2, 'tips': ' 密码错误，请重新输入 '}))
        else:
            # tips = ' 用户名不存在，请注册 '
            return HttpResponse(json.dumps(
                {'status': 3, 'tips': ' 用户名不存在，请注册 '}))
    return render(request, 'account/account_login.html', locals())


def account_logout(request):
    logout(request)
    return redirect('/blog/')


@csrf_exempt
def account_register(request):
    title = ' LFBlog 注册 '
    unit_2 = '/account/login/'
    unit_2_name = ' 立即登录 '
    unit_1 = '/account/setpassword'
    unit_1_name = ' 重置密码 '
    new_password = True
    password_tips = ' 重复密码 '
    register = True
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email_input', '')
        password = request.POST.get('password', '')
        re_password = request.POST.get('new_password', '')
        if User.objects.filter(username=username):
            return HttpResponse(json.dumps({'status': 1, 'tips': ' 用户名已存在 '}))
        elif not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
            return HttpResponse(json.dumps({'status': 2, 'tips': ' 邮箱格式不正确 '}))
        elif password != re_password:
            return HttpResponse(json.dumps({'status': 3, 'tips': ' 前后密码不同 '}))
        elif password == '' or len(password) < 6:
            return HttpResponse(json.dumps({'status': 4, 'tips': ' 密码不少于六位 '}))
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email)
            user.save()
            UserInfo.objects.create(user=user)
            UserToken.objects.create(user=user)
            token = jwt.encode({
                    'exp':datetime.utcnow()+timedelta(seconds=settings.TOKEN_EXPIRE_TIME),
                    'iat':datetime.utcnow(),
                    'data': {
                        'username': username
                    }
                },settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
            UserToken.objects.update_or_create(user=user, defaults={"token": token})
            login(request, user)
            # return redirect('/blog/')
            return HttpResponse(json.dumps(
                {'status': 5, 'tips': ' 注册成功,直接登录 ', 'token': token}))
            # tips = ' 注册成功 '
    return render(request, 'account/account_login.html', locals())


@csrf_exempt
def account_setpassword(request):
    username = request.user.username
    button = ' 获取验证码 '
    new_password = True
    title = 'LFBlog 修改密码'
    unit_2 = '/account/login/'
    unit_2_name = ' 立即登录 '
    unit_1 = '/account/register/'
    unit_1_name = ' 立即注册 '
    if request.method == 'POST':
        username = request.POST.get('username', '')
        code = request.POST.get('code', '')
        password = request.POST.get('password', '')
        re_password = request.POST.get('re_password', '')
        user = User.objects.filter(username=username)
        if not user:
            #tips =' 用户 '+username+' 不存在 '
            return HttpResponse(json.dumps(
                {'status': 1, 'tips': ' 用户 ' + username + ' 不存在 '}))
        else:
            if not request.session.get('code', ''):
                button = ' 重置密码 '
                tips = ' 验证码发送 '
                code = str(random.randint(1000, 9999))
                request.session['code'] = code
                user[0].email_user(' 找回密码 ', code)
                return HttpResponse(json.dumps(
                    {'status': 5, 'tips': tips, 'button': button}))
            elif code == request.session.get('code', ''):
                if password == re_password:
                    dj_ps = make_password(password, None, 'pbkdf2_sha256')
                    user[0].password = dj_ps
                    user[0].save()
                    del request.session['code']
                    login(request, user[0])
                    # return redirect('/blog/')
                    return HttpResponse(json.dumps(
                        {'status': 2, 'tips': ' 修改成功,直接登录 '}))
                else:
                    #tips = '前后密码不同 '
                    return HttpResponse(json.dumps(
                        {'status': 3, 'tips': ' 前后密码不同 '}))
            else:
                tips = ' 验证码错误，请重新获取 '
                del request.session['code']
                return HttpResponse(json.dumps(
                    {'status': 4, 'tips': ' 验证码错误，请重新获取 '}))
    return render(request, 'account/account_setpassword.html', locals())


@login_required(login_url='/account/login/')
def myself(request):
    user = request.user
    title = "{} 个人信息".format(user.username)
    userinfo = UserInfo.objects.get(user=user)
    return render(request, 'account/myself.html', locals())


def article_page(request, username):
    user = User.objects.get(username=username)
    article_titles = user.article_post.all()
    paginator = Paginator(article_titles, 6)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list
    articles_json = []
    for i in range(len(articles)):
        articles_json.append({'id': articles[i].id,
                              'title': articles[i].title,
                              'blog_img_url': articles[i].image_preview.url,
                              'updated': time.mktime(articles[i].updated.timetuple()),
                              'body': init_blog(articles[i].body[:150]),
                              'users_like': articles[i].users_like.count()})
    # return HttpResponse(serializers.serialize("json",articles))
    return HttpResponse(json.dumps(
        {'static': 200, 'data': articles_json, 'page_num': paginator.num_pages}))


@login_required(login_url='/account/login/')
@csrf_exempt
def myself_edit(request):
    user = request.user
    userinfo = UserInfo.objects.get(user=user)
    if request.method == 'POST':
        try:
            user.email = request.POST.get('email', '')
            userinfo.school = request.POST.get('school', '')
            userinfo.company = request.POST.get('company', '')
            userinfo.profession = request.POST.get('profession', '')
            userinfo.address = request.POST.get('address', '')
            userinfo.aboutme = request.POST.get('aboutme', '')
            user.save()
            userinfo.save()
            return HttpResponse(json.dumps({'status': 200, 'tips': '修改成功'}))
        except BaseException:
            return HttpResponse(json.dumps({'status': 500, 'tips': '修改失败'}))
    else:
        return render(request, "account/edit_myself.html", locals())


@login_required(login_url='/account/login/')
@csrf_exempt
def my_image(request):
    username = request.user.username
    if request.method == 'POST':
        uploadimg = request.FILES.get('uploadimg', '')
        print(type(uploadimg))
        userinfo = UserInfo.objects.get(user=request.user)
        avatorInfo = str(userinfo.photo).split('/')
        if avatorInfo[0] == 'default':
            pass
        else:
            if avatorInfo[1] == username + '.jpg':
                pass
            else:
                fname = '{}/{}'.format(settings.MEDIA_ROOT,
                                       str(userinfo.photo))
                try:
                    os.remove(fname)
                except Exception as e:
                    print(e)
        try:
            userinfo.photo.save(username + '.jpg', uploadimg)
            return HttpResponse(json.dumps(
                {'status': 200, 'tips': '上传成功', 'photo': userinfo.photo.url}))
        except BaseException:
            return HttpResponse(json.dumps({'status': 500, 'tips': '上传失败'}))
    else:
        return HttpResponse("该页面摸得GET")


@login_required(login_url='/account/login/')
@csrf_exempt
@require_POST
def get_avator(request):
    try:
        user = User.objects.get(username=request.POST.get('username'))
        userinfo = UserInfo.objects.get(user=user)
        print(userinfo.photo)
        if userinfo.photo:
            return HttpResponse(json.dumps(
                {'static': 200, 'photo': userinfo.photo.url}))
        else:
            return HttpResponse(json.dumps(
                {'static': 201, 'photo': '/media/default/default.jpg'}))
    except BaseException:
        return HttpResponse(json.dumps(
            {'static': 500, 'tips': 'Something error'}))


def author_info(request, username):
    title = "{} 个人信息".format(username)
    user = User.objects.get(username=username)
    userinfo = UserInfo.objects.get(user=user)
    return render(request, 'account/myself.html', locals())


def article_like(request, username):
    user = User.objects.get(username=username)
    articles = user.users_like.all()
    paginator = Paginator(articles, 6)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        article_list = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        article_list = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        article_list = current_page.object_list
    articles_json = []
    for i in range(len(article_list)):
        view = r.get('article:{}:views'.format(article_list[i].id))
        if view is None:
            view_count = 0
        else:
            view_count = view.decode('utf-8')
        articles_json.append({'id': article_list[i].id,
                              'title': article_list[i].title,
                              'blog_img_url': articles[i].image_preview.url,
                              'updated': time.mktime(article_list[i].updated.timetuple()),
                              'author': article_list[i].author.username,
                              'author_img_url': article_list[i].author.userinfo.photo_150x150.url,
                              'body': init_blog(article_list[i].body[:150]),
                              'users_like': article_list[i].users_like.count(),
                              'views': view_count})
    return HttpResponse(json.dumps(
        {'code': 201, 'data': articles_json, 'page_num': paginator.num_pages}))
