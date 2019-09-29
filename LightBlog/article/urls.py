from django.urls import path,re_path
from . import views
from . import list_views

app_name = 'article'

urlpatterns = [
    # 文章栏目
    path(r'article_column/', views.article_column, name='article_column'),
    # 文章栏目的重命名
    path('rename_article_column/', views.rename_article_column, name="rename_article_column"),
    # 删除栏目
    path('del_article_column/', views.del_article_column, name="del_article_column"),
    # 文章发布
    path('article_post/',views.article_post,name="article_post"),
    # 个人后台管理的文章列表
    path('article_list',views.article_list,name="article_list"),
    # 个人后台管理的文章查看
    re_path('article_detail/(?P<id>\d+)/', views.article_detail, name="article_detail"),
    # 删除文章
    path('del-article/', views.del_article, name="del_article"),
    # 修改文章
    path('redit-article/<int:article_id>/', views.redit_article, name="redit_article"),
    # 博客首页
    path('list_article_titles/',list_views.article_titles,name="article_titles"),
    # 博客页面
    path('article_content/<int:article_id>/',list_views.article_content,name="article_content"),
    # 博客评论的流加载
    path('article_comment/<int:article_id>/',list_views.comment_page, name="comment_page"),
    # 博客的点赞
    path('like_article/',views.like_article,name="like_article"),
    # 博客首页的流加载
    path('article_page/',list_views.article_page, name="article_page"),
    # 评论的点赞功能
    path('comment_like/',list_views.comment_like, name='comment_like'),
    # 评论的删除功能
    path('comment_delete',list_views.comment_delete, name='comment_delete')
]