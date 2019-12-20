from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
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


    # 主评论
    path('api/comment/post', views.comment_post),
    # 获取 博客评论
    path('api/comment/get', views.comments_get),
    # 删除 评论
    path('api/comment/del', views.comment_del),
    # 评论extra 信息
    path('api/comment/extra', views.comment_extra),
    # 评论点赞
    path('api/comment/like', views.comment_like),

    # 子评论
    path('api/comment_reply/post', views.comment_reply_post),
    # 获取更多的子评论
    path('api/comment_reply/more', views.comment_repy_more),


    # 获取检举类型list
    path('api/report/config/get', views.report_config),
    # 新增config
    path('api/report/config/add', views.add_config),
    # 删除
    path('api/report/config/del', views.del_config),
    path('api/report/config/detail', views.config_detail),
    path('api/report/config/update', views.edit_config),
]