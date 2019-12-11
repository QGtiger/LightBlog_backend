from django.shortcuts import render, get_object_or_404, HttpResponse
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .tasks import *
import json
import redis
import re
import time
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def init_blog(content):
    content_text1 = content.replace(
        '<p>',
        '').replace(
        '</p>',
        '').replace(
            "'",
        '')
    # 去掉图片链接
    content_text2 = re.sub(r'(!\[.*?\]\(.*?\))', '', content_text1)
    # 去掉markdown标签
    pattern = r'[\\\`\*\_\[\]\#\+\-\!\>]'
    content_text3 = re.sub(pattern, '', content_text2)
    return content_text3


def article_titles(request):
    return render(request, 'article/article_titles.html', locals())


def article_page(request):
    article_titles = ArticlePost.objects.all()
    paginator = Paginator(article_titles, 8)
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
    try:
        for i in range(len(articles)):
            view = r.get('article:{}:views'.format(articles[i].id))
            if view is None:
                view_count = 0
            else:
                view_count = view.decode('utf-8')
            articles_json.append({'id': articles[i].id,
                                'author': articles[i].author.username,
                                'author_img_url': articles[i].author.userinfo.photo_150x150.url,
                                'title': articles[i].title,
                                'updated': time.mktime(articles[i].updated.timetuple()),
                                'body': init_blog(articles[i].body[:200]),
                                'users_like': articles[i].users_like.count(),
                                'views': view_count,
                                'blog_img_url': articles[i].image_preview.url})
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'success': False, 'tips': 'something error'}))
    # return HttpResponse(serializers.serialize("json",articles))
    return HttpResponse(json.dumps(
        {'static': 200, 'data': articles_json, 'page_num': paginator.num_pages, "success": True}))


@csrf_exempt
def article_content(request, article_id):
    if request.method == 'POST':
        if request.user.username == "":
            return HttpResponse(json.dumps(
                {'code': 502, 'tips': 'What are u doing now??'}))
        comment = request.POST.get('comment', '')
        if comment.strip() == '':
            return HttpResponse(json.dumps(
                {'code': 403, 'tips': '评论内容不能为空...'}))
        try:
            user = request.user
            article = get_object_or_404(ArticlePost, id=article_id)
            C = Comment(article=article, commentator=user, body=comment)
            C.save()
            comment_info = {
                'commentator': user.username,
                'commentator_img_url': user.userinfo.photo_150x150.url,
                'id': C.id,
                'body': C.body,
                'created': time.mktime(
                    C.created.timetuple())}
            return HttpResponse(json.dumps(
                {"code": 200, "tips": "感谢您的评论", 'comment_info': comment_info}))
        except BaseException:
            return HttpResponse(json.dumps({"code": 501, "tips": "评论系统出现错误"}))
    else:
        article = get_object_or_404(ArticlePost, id=article_id)
        total_views = r.incr("article:{}:views".format(article_id))
        r.zincrby('article_ranking', 1, article_id)
        is_like = False
        if request.user.username:
            user = request.user
            if user in article.users_like.all():
                is_like = True
        return render(request, "article/article_content.html", locals())


@login_required(login_url='/account/login')
@require_POST
@csrf_exempt
def comment_like(request):
    user = request.user
    comment_id = request.POST.get("id", "")
    action = request.POST.get("action", "")
    if comment_id and action:
        try:
            comment = Comment.objects.get(id=comment_id)
            if action == 'like':
                comment.comment_like.add(user)
                num = comment.comment_like.count()
                return HttpResponse(json.dumps(
                    {'static': 200, 'support_num': num}))
            else:
                comment.comment_like.remove(user)
                num = comment.comment_like.count()
                return HttpResponse(json.dumps(
                    {'static': 201, 'support_num': num}))
        except BaseException:
            return HttpResponse(json.dumps(
                {'static': 500, 'tips': '系统错误,重新尝试'}))


@csrf_exempt
@require_POST
def comment_delete(request):
    comment_id = request.POST['id']
    comment = Comment.objects.get(id=comment_id)
    try:
        if request.user == comment.commentator:
            comment_delete_task.delay(comment_id)
            return HttpResponse(json.dumps({'static': 201, 'tips': '评论已删除'}))
        else:
            return HttpResponse(json.dumps(
                {'static': 502, 'tips': "You don't have permission.."}))
    except BaseException:
        return HttpResponse(json.dumps(
            {'static': 500, 'tips': 'Something Error...'}))


def init_data(data):
    items = data.comment_reply.all()[:2]
    list_data = []
    for item in items:
        if item.reply_type == 0:
            list_data.append({'from': item.comment_user.username,
                              'from_img_url': item.comment_user.userinfo.photo_150x150.url,
                              'to': data.commentator.username,
                              'id': item.id,
                              'body': item.body if item.is_deleted is False else '评论已删除',
                              'created': time.mktime(item.created.timetuple())})
        else:
            to_id = item.reply_comment
            list_data.append({'from': item.comment_user.username,
                              'from_img_url': item.comment_user.userinfo.photo_150x150.url,
                              'to': Comment_reply.objects.get(id=to_id).comment_user.username,
                              'id': item.id,
                              'body': item.body if item.is_deleted is False else '评论已删除',
                              'created': time.mktime(item.created.timetuple())})
    return list_data


def comment_page(request, article_id):
    article = get_object_or_404(ArticlePost, id=article_id)
    comments_all = article.comments.all()
    paginator = Paginator(comments_all, 6)
    page = request.GET['page']
    try:
        current_page = paginator.page(page)
        comments = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        comments = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        comments = current_page.object_list
    comments_list = []
    for item in comments:
        comments_list.append({'id': item.id,
                              'commentator': item.commentator.username,
                              'commentator_img_url': item.commentator.userinfo.photo_150x150.url,
                              'comment_reply': init_data(item),
                              'created': time.mktime(item.created.timetuple()),
                              'comment_like': item.comment_like.count(),
                              'body': item.body if item.is_deleted is False else '评论已删除'})
    return HttpResponse(json.dumps(
        {'code': 200, 'res': comments_list, 'page_num': paginator.num_pages}))
