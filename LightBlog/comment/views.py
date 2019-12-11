from django.shortcuts import render,HttpResponse
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST,require_http_methods,require_GET
import json
import math
import time


# Create your views here.
@csrf_exempt
@require_POST
def comment_reply(request):
    reply_type = request.POST.get('reply_type','')
    if reply_type == '0':
        id = request.POST.get('id','')
        body = request.POST.get('body','')
        if body.strip() == '':
            return HttpResponse(json.dumps({'code':201,'tips':'内容不能为空'}))
        else:
            try:
                comment = Comment.objects.get(id=id)
                user = request.user
                if user == comment.commentator:
                    return HttpResponse(json.dumps({'code':202,'tips':'别搞我'}))
                Com = Comment_reply(comment_reply=comment, comment_user=user, commented_user=comment.commentator, body=body)
                Com.save()
                comment_info = {'from': user.username,'from_img_url':user.userinfo.photo_150x150.url,'to':comment.commentator.username , 'id': Com.id, 'body': Com.body,
                                'created': time.mktime(Com.created.timetuple())}
                return HttpResponse(json.dumps({'code':203, 'tips':'评论成功', 'res':comment_info}))
            except:
                return HttpResponse(json.dumps({"code": 501, "tips": "评论系统出现错误"}))
    else:
        comment_id = request.POST.get('comment_id','')
        id = request.POST.get('id', '')
        body = request.POST.get('body', '')
        if body.strip() == '':
            return HttpResponse(json.dumps({'code':201,'tips':'内容不能为空'}))
        else:
            try:
                comment = Comment.objects.get(id=comment_id)
                comment_reply = Comment_reply.objects.get(id=id)
                user = request.user
                if user == comment_reply.comment_user:
                    return HttpResponse(json.dumps({'code':202,'tips':'别搞我'}))
                Com = Comment_reply(comment_reply=comment, reply_type=1, comment_user=user, reply_comment=id, commented_user=comment_reply.comment_user, body=body)
                Com.save()
                comment_info = {'from': user.username,'from_img_url':user.userinfo.photo_150x150.url, 'to': comment_reply.comment_user.username, 'id': Com.id, 'body': Com.body,
                                'created': time.mktime(Com.created.timetuple())}
                return HttpResponse(json.dumps({'code': 203, 'tips': '评论成功', 'res': comment_info}))
            except:
                return HttpResponse(json.dumps({"code": 501, "tips": "评论系统出现错误"}))


## 评论删除
@csrf_exempt
@require_POST
def comment_reply_delete(request):
    id = request.POST.get('id','')
    comment_reply = Comment_reply.objects.get(id=id)
    try:
        if request.user == comment_reply.comment_user:
            comment_reply.is_deleted = True
            comment_reply.save()
            return HttpResponse(json.dumps({'code':201,'tips':'评论已删除'}))
        else:
            return HttpResponse(json.dumps({'code':502,'tips':'You do not have permission...'}))
    except:
        return HttpResponse(json.dumps({'code':203,'tips':'Something error...'}))


def init_data(data):
    items = data.comment_reply.all()
    list_data = []
    for item in items:
        if item.reply_type == 0:
            list_data.append({'from': item.comment_user.username,'from_img_url':item.comment_user.userinfo.photo_150x150.url, 'to':data.commentator.username , 'id': item.id, 'body': item.body if item.is_deleted is False else '评论已删除',
                            'created': time.mktime(item.created.timetuple())})
        else:
            to_id = item.reply_comment
            list_data.append(
                {'from': item.comment_user.username,'from_img_url':item.comment_user.userinfo.photo_150x150.url, 'to': Comment_reply.objects.get(id=to_id).comment_user.username,'id': item.id, 'body': item.body if item.is_deleted is False else '评论已删除',
                 'created': time.mktime(item.created.timetuple())})
    return list_data


@csrf_exempt
@require_POST
def comment_reply_get(request):
    id = request.POST.get('id','')
    comment = Comment.objects.get(id=id)
    comment_root = {'id':comment.id, 'commentator': comment.commentator.username,'commentator_img_url': comment.commentator.userinfo.photo_150x150.url, 'created': time.mktime(comment.created.timetuple()), 'comment_like': comment.comment_like.count(), 'body': comment.body if comment.is_deleted is False else '评论已删除'}
    comment_child = init_data(comment)
    length = len(comment_child)
    return HttpResponse(json.dumps({'code':201,'comment_root': comment_root, 'comment_child': comment_child, 'nums':length}))


@login_required(login_url='/account/login/')
def message(request):
    return render(request, 'comment/notifications.html')


@require_GET
def notifications(request):
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except:
        page = 1
    user = request.user
    articles = user.article_post.all()
    response = []
    for article in articles:
        comments = article.comments.all()
        for comment in comments:
            comment.is_read = 1
            comment.save()
            if user == comment.commentator:
                continue
            if comment.is_deleted is False:
                response.append({'commentator':comment.commentator.username,'commentator_img_url': comment.commentator.userinfo.photo_150x150.url, 'article_title': article.title, 'time': time.mktime(comment.created.timetuple()), 'body': comment.body[:50], 'comment_root_id': comment.id, 'article_id': article.id})
    response.sort(key=lambda x: x['time'], reverse=True)
    nums = math.ceil(len(response)/6.0)
    if page > nums:
        page = nums
    res = response[6*(page-1):6*page]
    return HttpResponse(json.dumps({'code':201, 'res':res, 'nums':nums}))


@require_GET
def is_read_comments(request):
    user = request.user
    articles = user.article_post.all()
    count = 0
    for article in articles:
        comments = article.comments.all()
        for comment in comments:
            if user == comment.commentator:
                comment.is_read = 1
                comment.save()
                continue
            elif comment.is_read == 0 and comment.is_deleted is False:
                count += 1
    commented_comments = user.commented_user.all()
    commented_count = 0
    for comment in commented_comments:
        if comment.is_read == 0 and comment.is_deleted is False:
            commented_count += 1
    return HttpResponse(json.dumps({'code':201, 'nums':count, 'commented_nums': commented_count}))


@login_required(login_url='/account/login/')
@require_GET
def comments(request):
    user = request.user
    commenteds = user.commented_user.all()
    res = []
    for comment in commenteds:
        comment.is_read = 1
        comment.save()
        if comment.is_deleted is False:
            res.append({'commentator': comment.comment_user.username,'commentator_img_url': comment.comment_user.userinfo.photo_150x150.url, 'article_title': comment.comment_reply.article.title, 'time': time.mktime(comment.created.timetuple()), 'body': comment.body[:50],'comment_root_id': comment.comment_reply.id, 'comment_child_id': comment.id, 'article_id': comment.comment_reply.article.id})
    res.sort(key=lambda x: x['time'], reverse=True)
    return render(request, 'comment/comments.html', {'comments': res})

