from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
    # 评论的回复
    path(r'comment_reply', views.comment_reply, name="comment_reply"),
    # 评论的删除
    path(r'comment_reply_delete', views.comment_reply_delete, name="comment_reply_delete"),
    # 评论查看回复
    path(r'comment_reply/get',views.comment_reply_get, name="comment_reply_get"),
    # 个人消息页面
    path(r'message', views.message, name="message"),
    # 博客评论消息的流加载
    path(r'notifications', views.notifications, name="notifications"),
    # 个人消息是否查看的API
    path(r'is_read_comments', views.is_read_comments, name="is_read_comments"),
    # 评论的评论的消息
    path(r'notifications/comments', views.comments, name="comments"),
]