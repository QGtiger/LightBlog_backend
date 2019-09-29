# LightBlog 博客

>LightBlog博客系统是我用了近四五周写的一个基于Django的博客系统，基本的功能也是正常博客所拥有的，如用户方面有登录注册，修改密码，个人的首页，个人信息修改，头像剪切上传，个人博客页面，个人博客的编写(基于markdown)。博客方面：用于可以为自己写的博客加栏目分类，博客上传后也是展示在首页，博客也是可以在线修改，有博客点赞功能和简单评论功能等等。前端页面是用一个很小的前端框架搭建——layui。由于该博客有好的方面也有带改进的方面，所以这里就不多一一阐述，该这篇博客也是会一直置顶，更改。欢迎来踩踩(别踩坏了)——[LightBlog博客](http://blog.qnpic.top/blog)

<!-- more -->

>夭寿啦，本博客已成功从windows服务器上向ubuntu服务器完成转移，历时好几个小时。主要是mysqlclient这个模块也太难装了。QAQ不管怎么说也是成功转移。也是在原来的基础上做了点界面修改和ajax动态修改，还完成了聊天室的功能和评论删除等功能。

## 1.评论动态添加和删除

>在评论的时候我原本是发出评论就前端界面刷新已完成加载，这次也是无聊进行了优化，用ajax动态加载

>1.首页是后端代码的实现，至于路由的 选择这里就不加阐述了，Just show code

```
from django.shortcuts import render,get_object_or_404,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ArticlePost,Comment
from django.conf import settings
import json


@csrf_exempt
def article_content(request, article_id):
    article = get_object_or_404(ArticlePost, id=article_id)
    if request.method == 'POST':
        comment = request.POST.get('comment','')
        user = request.user
        try:
            C = Comment(article=article,commentator=user,body=comment)
            C.save()
            comment_info = {'commentator':user.username,'id': C.id, 'body': C.body, 'created': C.created.strftime("%Y-%m-%d %H:%M:%S")}
            return HttpResponse(json.dumps({"static":200,"tips":"感谢您的评论", 'comment_info':comment_info}))
        except:
            return HttpResponse(json.dumps({"static":500,"tips":"评论系统出现错误"}))
    else:
        total_views = r.incr("article:{}:views".format(article_id))
        r.zincrby('article_ranking', 1, article_id)
        comments = Comment.objects.filter(article=article)
        return render(request, "article/article_content.html", locals())
```

>上述的视图函数也是接收数据后创建数据库对象，然后后端处理数据向前端传送数据已构造前端界面。前端接收数据和发送数据的函数如下

```
$('.comment-btn').on('click',function(){
    if($('.username').val()==''){
        layer.msg('请先登录')
    }else{
        var comment = $('.comment_text').val();
        $.ajax({
            url: '{% url "article:article_content" article.id %}',
            type: "POST",
            data: {'comment':comment },
            success: function(e){
                $('.comment_text').val('');
                res = JSON.parse(e);
                if(res.static='200'){
                    console.log(res);
                    commentator = res.comment_info;
                    prepend_li='<li onmouseenter="EnterFunction(this)" onmouseleave="LeaveFunction(this)">'+
                '<div class="commentator">'+
                    '<div class="commentator-img">'+
                        '<a href="/account/author/'+commentator.commentator+'">'+
                            '<img src="/media/avator/'+commentator.commentator+'.jpg" class="layui-nav-img" alt="">'+
                        '</a>'+
                    '</div>'+
                    '<div class="commentator-info">'+
                        '<a href="/account/author/'+commentator.commentator+'">'+commentator.commentator+'</a>'+
                        '<span style="margin-left:20px">'+commentator.created+'</span>'+
                        '<span style="margin-left:20px"> 人气值: <span class="support-comment">0</span></span>'+
                    '</div>'+
                    '<div class="comment-wrap">'+
                        '<p>'+commentator.body+'</p>'+
                    '</div>'+
                    '<div class="meta">'+
                        '<span onclick="comment_like('+commentator.id+',\'like\',this)"><span><i class="layui-icon layui-icon-praise"></i> <span class="comment-like">赞</span></span></span>'+
                        '<span onclick="comment_like('+commentator.id+',\'unlike\',this)"><span><i class="layui-icon layui-icon-tread"></i> <span class="comment-unlike">踩</span></span></span>'+
                        '<a href="javascript:void(0)" onclick="comment_delete('+ commentator.id +', this)" class="comment-tool comment-delete">删 除</a>'+
                    '</div>'+
                '</div>'+
            '</li>'

                    $('.history-comment ul').prepend(prepend_li);
                }else{
                    layer.msg(res.tips);
                }
            }
        })
    }
})
```

>其实这件那一大串js代码只是构造评论标签，好动态加载上去，中间几个函数你可以不用管，你主要的是知道这前后端结合的工作流程~~~(别问，问我也没法告诉你,我不会告诉你aboutme 有点联系方式)

>流程也是蛮简单的，签单单击发送，触发js函数，向后端发送请求和数据，后端接收，然后进行验证和数据库的操作，然后向前端发送response，前端接收和进行响应。是不是很简单呀~~

### 评论删除

>眼尖的应该就出来了，评论删除的功能也是类似，这里也是对用户交互之间做了优化，如，鼠标移动到之间的评论是删除，也别人的评论是举报。实现前端代码如下：

```
function EnterFunction(e){
    $(e).find('.comment-tool').css('display','block');
} //移动到评论内就显示

function LeaveFunction(e){
    $(e).find('.comment-tool').css('display','none');
} //移动出就隐藏

//点击事件
function comment_delete(id, e){
    if($('.username').val()==''){
        layer.msg('请先登录')
    }else{
        layer.confirm('确定要删除该评论?',{
            btn: ['确定', '取消']
        },function(){
            $.ajax({
                url: "{% url 'article:comment_delete' %}",
                method: "POST",
                data: {'id':id},
                dataType: 'json',
                success: function(res){
                    if(res.static=='201'){
                        dom = $(e).parent().parent().parent();
                        dom.remove();
                        layer.msg(res.tips,{icon:1})
                    }else if(res.static=='502'){
                        layer.msg(res.tips,{icon:2})
                    }else{
                        layer.msg(res.tips)
                    }
                }
            })
        })
    }
}
```

>后端代码

```
@csrf_exempt
@require_POST
def comment_delete(request):
    comment_id = request.POST['id']
    comment = Comment.objects.get(id=comment_id)
    try:
        if(request.user == comment.commentator):
            comment.delete()
            return HttpResponse(json.dumps({'static':201, 'tips':'评论已删除'}))
        else:
            return HttpResponse(json.dumps({'static':502, 'tips':"You don't have permission.."}))
    except:
        return HttpResponse(json.dumps({'static':500, 'tips':'Something Error...'}))
```

>当当，这就是这是实现的代码系不系很简单，主要是思路，嘻嘻，下面是实现的效果

![img](http://qnpic.top/blog_comment%5CGIF.gif)

## Redis 简单实现文章浏览次数

>关于redis的基本语法，我上几篇也是简单介绍过了。这次也算是一次简单的运用

>1.首先在settings.py文件中做好数据库的配置

```
#redis配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_DB = 0
```

>2.在视图函数中和redis建立连接

```
import redis

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
```

>3.修改文章页面的视图函数,只需要看GET请求，POST请求是评论

```
@csrf_exempt
def article_content(request, article_id):
    article = get_object_or_404(ArticlePost, id=article_id)
    if request.method == 'POST':
        comment = request.POST.get('comment','')
        user = request.user
        try:
            C = Comment(article=article,commentator=user,body=comment)
            C.save()
            return HttpResponse(json.dumps({"static":200,"tips":"感谢您的评论"}))
        except:
            return HttpResponse(json.dumps({"static":500,"tips":"评论系统出现错误"}))
    else:
        total_views = r.incr("article:{}:views".format(article_id))
        r.zincrby('article_ranking', 1, article_id)
        comments = Comment.objects.filter(article=article)
        return render(request, "article/article_content.html", locals())
```

>4.然后在相应的模板文件内添加

```
<span style="margin-left:20px">{{ total_views }} view{{ total_views|pluralize }}</span>
```

>5.效果如下：

![img](http://qnpic.top/blog_redis_view%5C1.jpg)

## redis 简单实现博客的最受欢迎文章

>修改博客首页的视图函数

```
def article_titles(request):
    length = r.zcard('article_ranking')
    article_ranking = r.zrange("article_ranking", 0, length, desc=True)[:5]
    article_ranking_ids = [int(id) for id in article_ranking]
    most_viewed = list(ArticlePost.objects.filter(id__in=article_ranking_ids))
    most_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))
    return render(request,'article/article_titles.html',locals())
```

>然后在模板内增加相应的展示代码

```
<div class="article_ranking" style="margin:20px 40px">
        <h3>最受欢迎文章</h3>
        <ol>
            {% for article in most_viewed %}
            <li><a href="{% url 'article:article_content' article.id %}">{{ forloop.counter }}. {{ article.title }}</a></li>
            {% endfor %}
        </ol>
    </div>
```

>实现效果

![img](http://qnpic.top/blog_redis_view%5C2.jpg)

## 对博客评论的评论

>1.首先是在models.py里编写数据库代码，结构如下

```
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# 在article app下的models里引用相对应的model
from article.models import Comment, ArticlePost


class Comment_reply(models.Model):
    comment_reply = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_reply") # 回复的主评论
    reply_type = models.IntegerField(default=0) # 回复的类型，0为主评论，1为评论下的评论
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentator_reply") # 回复人
    commented_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commented_user", blank=True, null=True)# 被回复的人
    created = models.DateTimeField(default=timezone.now)
    body = models.TextField()
    reply_comment = models.IntegerField(default=0) # 回复那条评论，id
    is_read = models.IntegerField(default=0) # 是否查看，为了应对后面的消息系统

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "Comment by {} on {}".format(self.comment_user, self.created)
```

>2.记得编写完了后生成数据库表，`python manage.py makemigrations` , `python manage.py migrate`

>3.然后编写前端代码，向后端动态发送数据

```
$('body').on('click', '.comment-reply-btn', function(e){
        if($('.username').val()==''){
            layer.msg('请先登录')
        }else{
            var dom = $(this).parent().parent().parent();
            if(dom.parent().hasClass('commentator-root')){
                data = {'reply_type': 0,'id': dom.attr('comment_id'), 'body': dom.children("#textarea").val()}
            }else if(dom.parent().hasClass('commentator-child')){
                data = {'reply_type': 1, 'comment_id': dom.parent().parent().attr('comment_id'), 'id':dom.attr('comment_id'), 'body': dom.children("#textarea").val()}
            }else{
                layer.msg('别搞我呀..');
                return;
            }
            console.log(data)
            $.ajax({
                url: "{% url 'comment:comment_reply' %}",
                method: "POST",
                dataType: "json",
                data: data,
                success: function(res){
                    if(res.code=='203'){
                        console.log(res.res)
                        layer.msg(res.tips);
                        dom.html('')
                        //console.log(dom)
                        dom.prev().find(".tool-reply").text('回 复')
                        data = res.res
                        item = '<div class="commentator commentator-child" id="comment-child-'+data.id+'" onmouseenter="EnterFunction(this)" onmouseleave="LeaveFunction(this)">'+
                        '<div class="commentator-img">'+
                            '<a href="/account/author/'+data.from+'">'+
                                '<img src="/media/avator/'+data.from+'.jpg" class="layui-nav-img" alt="">'+
                            '</a>'+
                        '</div>'+
                        '<div class="commentator-info">'+
                            '<a href="/account/author/'+data.from+'" class="commentator-name">'+data.from+'</a>'+
                            '<span style="margin:0 10px">回复</span>'+
                            '<a href="/account/author/'+data.to+'">'+data.to+'</a>'+
                            '<span style="margin-left:20px">'+ data.created+'</span>'+
                        '</div>'+
                        '<div class="comment-wrap">'+
                            '<pre>'+data.body+'</pre>'+
                        '</div>'+
                        '<div class="meta">'+
                            '<a href="javascript:void(0)" onclick="comment_reply_delete('+data.id+', this)" class="comment-tool comment-delete"><span><i class="layui-icon layui-icon-delete"></i> <span>删 除</span></span></a>'+
                        '</div>'+
                        '<div class="reply_input" comment_id="'+data.id+'"></div>'+
                    '</div>'
                        dom.parent().parent().find('.commentator-root').after($(item))
                        is_reply = 0;
                    }else{
                        layer.msg(res.tips);
                    }
                }
            })
        }

    })
```

>4.以上代码就是判断是否是主评论，来改变向后端传输的数据。后端编写路由和视图函数，视图函数如下，路由就不展示了

```
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from article.models import Comment
from .models import Comment_reply
import json

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
                comment_info = {'from': user.username,'to':comment.commentator.username , 'id': Com.id, 'body': Com.body,
                                'created': Com.created.strftime("%Y-%m-%d %H:%M:%S")}
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
                comment_info = {'from': user.username, 'to': comment_reply.comment_user.username, 'id': Com.id, 'body': Com.body,
                                'created': Com.created.strftime("%Y-%m-%d %H:%M:%S")}
                return HttpResponse(json.dumps({'code': 203, 'tips': '评论成功', 'res': comment_info}))
            except:
                return HttpResponse(json.dumps({"code": 501, "tips": "评论系统出现错误"}))

```

>以上就是Django后端的处理函数，可能有些地方并不是很好，后期再改进。后端处理完数据并数据库保存好后，返回数据，前端接收到后，也是ajax动态加载上去。

>这里主要也是简单的前后端结合实现动态加载，难的是后端的数据库逻辑，So，show you the pic。

![img](http://qnpic.top/commented.gif)

<br><br><br>其实主要还是redis相应的函数需要理解，So<br><br>Just have fun..
