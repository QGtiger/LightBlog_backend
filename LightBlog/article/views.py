from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import ArticleColumn, ArticlePost
from .forms import ArticleColumnForm, ArticlePostForm
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from .tasks import *
import json
import re
import requests
from django.core.files.base import ContentFile


# Create your views here.
@login_required(login_url='/account/login/')
@csrf_exempt
def article_column(request):
    user = request.user
    if request.method == 'GET':
        columns = ArticleColumn.objects.filter(user=user)
        # column_form = ArticleColumnForm()
        return render(request, 'article/article_column.html', locals())
    if request.method == 'POST':
        column_name = request.POST['column']
        columns = ArticleColumn.objects.filter(user=user, column=column_name)
        if columns:
            return HttpResponse('2')
        else:
            ArticleColumn.objects.create(user=user, column=column_name)
            return HttpResponse('1')


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def rename_article_column(request):
    column_name = request.POST["column_name"]
    column_id = request.POST['column_id']
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.column = column_name
        line.save()
        return HttpResponse("1")
    except BaseException:
        return HttpResponse("0")


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def del_article_column(request):
    column_id = request.POST["column_id"]
    try:
        line = ArticleColumn.objects.get(id=column_id)
        line.delete()
        return HttpResponse("1")
    except BaseException:
        return HttpResponse("2")


@login_required(login_url='/account/login/')
@csrf_exempt
def article_post(request):
    user = request.user
    if request.method == 'POST':
        data = request.POST
        article_post_form = ArticlePostForm(data=data)
        if article_post_form.is_valid():
            cd = article_post_form.cleaned_data
            try:
                new_article = article_post_form.save(commit=False)
                new_article.author = user
                new_article.column = user.article_column.get(
                    id=request.POST['column_id'])
                new_article.word_count = len(data.get('body', ''))
                new_article.save()
                imgs = re.findall(
                    re.compile(r'!\[.*?\]\((.*?)\)'), data.get('body',''))
                if len(imgs) > 0:
                    try:
                        content = ContentFile(requests.get(imgs[0]).content)
                        new_article.image_preview.save(str(new_article.id) + '.jpg', content)
                    except Exception as e:
                        print(e)
                return HttpResponse('1')
            except BaseException as e:
                print(e)
                return HttpResponse('2')
        else:
            return HttpResponse('3')
    else:
        article_post_form = ArticlePostForm()
        article_columns = user.article_column.all()
        return render(request, 'article/article_post.html', locals())


@login_required(login_url='/account/login/')
def article_list(request):
    user = request.user
    articles_list = ArticlePost.objects.filter(author=user)
    paginator = Paginator(articles_list, 6)
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
    return render(request, 'article/article_list.html', locals())


@login_required(login_url='/account/login/')
def article_detail(request, id):
    article = get_object_or_404(ArticlePost, id=id)
    user = request.user
    if user.username != article.author.username:
        return HttpResponse('You do not have permission!')
    return render(request, "article/article_detail.html", locals())


@login_required(login_url='/account/login/')
@require_POST
@csrf_exempt
def del_article(request):
    article_id = request.POST['article_id']
    article = ArticlePost.objects.get(id=article_id)
    user = request.user
    if user.username != article.author.username:
        return HttpResponse('You do not have permission!')
    try:
        article = ArticlePost.objects.get(id=article_id)
        article.delete()
        return HttpResponse("1")
    except BaseException:
        return HttpResponse("2")


@login_required(login_url='/account/login')
@csrf_exempt
def redit_article(request, article_id):
    article = ArticlePost.objects.get(id=article_id)
    user = request.user
    if user.username != article.author.username:
        return HttpResponse('You do not have permission!')
    if request.method == "GET":
        article_columns = user.article_column.all()
        # this_article_form = ArticlePostForm(initial={"title": article.title})
        this_article_column = article.column
        return render(request,
                      "article/redit_article.html",
                      {"article": article,
                       "article_columns": article_columns,
                       "this_article_column": this_article_column})
    else:
        redit_article = ArticlePost.objects.get(id=article_id)
        try:
            redit_article.column = user.article_column.get(
                id=request.POST['column_id'])
            redit_article.title = request.POST['title']
            redit_article.body = request.POST['body']
            redit_article.save()
            return HttpResponse("1")
        except BaseException:
            return HttpResponse("2")


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def like_article(request):
    user = request.user
    article_id = request.POST.get('id', '')
    action = request.POST.get('action')
    if article_id and action:
        try:
            article = ArticlePost.objects.get(id=article_id)
            article_likes = article.users_like.all()
            if action == 'like':
                for item in article_likes:
                    if item == user:
                        return HttpResponse(json.dumps(
                            {'static': 200, 'tips': '不能重复点┗|｀O′|┛ 嗷~~~，亲[呕]^-^'}))
                article.users_like.add(user)
                num = article.users_like.count()
                return HttpResponse(json.dumps(
                    {'static': 201, 'tips': '感谢您的喜爱', 'num': num, 'user': user.username}))
            else:
                article.users_like.remove(user)
                num = article.users_like.count()
                return HttpResponse(json.dumps(
                    {'static': 202, 'tips': '我会努力的', 'num': num, 'user': user.username}))
        except BaseException:
            return HttpResponse(json.dumps(
                {'static': 500, 'tips': '系统错误,重新尝试'}))


# 404,505页面
def page_not_found(request, exception):
    return render(request, '404/error404.html', status=404)
