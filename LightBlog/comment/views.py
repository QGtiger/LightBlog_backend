from django.shortcuts import render,HttpResponse
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST,require_http_methods,require_GET
from django.contrib.auth.models import User
from .models import LightBlogComment,LightBlogComment_reply
from article.models import LightBlogArticle
import json
import math
import time
import jwt
from django.conf import settings
from article.utils import get_username


def is_liked(user, comment):
    return comment in user.comment_like.all()


def is_reply_liked(user, comment):
    return comment in user.comment_reply_like.all()


def init_data(user, data):
    items = data.lightblogcomment_reply.all()
    list_data = []
    for item in items:
        if item.reply_type == 0:
            list_data.append({'from': item.comment_user.username,'from_img_url':item.comment_user.userinfo.photo_150x150.url, 'to':data.commentator.username , 'id': item.id, 'comment_text': comment_text(item),
                            'created': time.mktime(item.created.timetuple()),
                              'comment_like': item.comment_reply_like.count(),
                              'is_liked': is_reply_liked(user, item)
                              })
        else:
            to_id = item.reply_comment
            list_data.append(
                {'from': item.comment_user.username,'from_img_url':item.comment_user.userinfo.photo_150x150.url, 'to': item.commented_user.username,'id': item.id, 'comment_text': comment_text(item),
                 'created': time.mktime(item.created.timetuple()),
                 'comment_like': item.comment_reply_like.count(),
                 'is_liked': is_reply_liked(user, item)
                 })
    return list_data


def comment_post(request):
    try:
        blogId = request.POST.get('blogId', '')
        commentator_name = request.POST.get('commentatorName', '')
        comment_text = request.POST.get('commentText', '')
        commentator = User.objects.get(username=commentator_name)
        article = LightBlogArticle.objects.get(id=blogId)
        comment = LightBlogComment(article=article,commentator=commentator,comment_text=comment_text)
        comment.save()
        comment_info = {
            "commentator": commentator_name,
            "commentator_img_url": commentator.userinfo.photo_150x150.url,
            "id": comment.id,
            "created": time.mktime(
                    comment.created.timetuple()),
            "comment_like": comment.comment_like.count(),
            "comment_text": comment_text,
            "is_liked": False
        }
        return HttpResponse(json.dumps({"success": True, "tips": "OK", "data": comment_info}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def comment_text(comment):
    if comment.deleted_by_admin:
        return '该评论已被举报、删除'
    elif comment.is_deleted:
        return '该评论已被删除'
    else:
        return comment.comment_text


def comments_get(request):
    try:
        blogId = request.POST.get('blogId', '')
        blog = LightBlogArticle.objects.get(id=blogId)
        comments_all = blog.lightblog_comment.all()
        paginator = Paginator(comments_all, 6)
        page = request.GET['page']

        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
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
            comments_list.append({
                "comment_root": {
                    'id': item.id,
                    'commentator': item.commentator.username,
                    'commentator_img_url': item.commentator.userinfo.photo_150x150.url,
                    'created': time.mktime(item.created.timetuple()),
                    'comment_like': item.comment_like.count(),
                    'comment_text': comment_text(item),
                    'is_liked': is_liked(user, item)
                },
                'comment_reply': init_data(user,item),
            })
        return HttpResponse(json.dumps(
            {'success': True, 'data': comments_list, 'page_num': paginator.num_pages}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))


def comment_del(request):
    try:
        commentId = request.POST.get('commentId', '')
        commentType = request.POST.get('commentType', '') # 1为主评论， 2为子评论
        requestUser = get_username(request)
        if commentType == '1':
            comment = LightBlogComment.objects.get(id=commentId)
            if requestUser != comment.commentator and requestUser.is_superuser is False:
                return HttpResponse(json.dumps({"success": False, "tips": "您没有权限删除"}))
        else:
            comment = LightBlogComment_reply.objects.get(id=commentId)
            if requestUser != comment.comment_user and requestUser.is_superuser is False:
                return HttpResponse(json.dumps({"success": False, "tips": "您没有权限删除"}))
        comment.is_deleted = True
        comment.save()
        return HttpResponse(json.dumps({"success": True, "tips": "ok"}))
    except Exception as e:
        return HttpResponse(json.dumps({"success": False, "tips": str(e)}))



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

