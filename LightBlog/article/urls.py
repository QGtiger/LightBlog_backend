from django.urls import path,re_path
from . import views
from . import list_views
from . import lightblog_views
from . import personalColumn
from . import articleViews

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
    path('article_content/<int:article_id>',list_views.article_content,name="article_content"),
    # 博客评论的流加载
    path('article_comment/<int:article_id>/',list_views.comment_page, name="comment_page"),
    # 博客的点赞
    path('like_article/',views.like_article,name="like_article"),
    # 博客首页的流加载
    path('article_page',list_views.article_page, name="article_page"),
    # 评论的点赞功能
    path('comment_like/',list_views.comment_like, name='comment_like'),
    # 评论的删除功能
    path('comment_delete',list_views.comment_delete, name='comment_delete'),

    # 获取专栏
    path('api/get/special_column', lightblog_views.special_column),
    # 增加专栏
    path('api/add/special_column', lightblog_views.add_special_column),
    # 删除专栏
    path('api/del/special_column', lightblog_views.del_special_column),
    # 专栏详情
    path('api/detail/special_column', lightblog_views.special_column_detail),
    # 修改专栏
    path('api/update/special_column', lightblog_views.update_special_column),
    # 发布专栏
    path('api/publish/special_column', lightblog_views.publish_special_column),
    # 下架专栏
    path('api/down/special_column', lightblog_views.down_special_column),
    # 获取专题list
    path('api/get/special_theme', lightblog_views.special_theme),
    # 新增专题
    path('api/add/special_theme', lightblog_views.add_special_theme),
    # 删除专题
    path('api/del/special_theme', lightblog_views.del_special_theme),
    # 专题详情
    path('api/detail/special_theme',lightblog_views.detail_special_theme),
    # 更新专题
    path('api/update/special_theme', lightblog_views.update_special_theme),
    # 发布专题
    path('api/publish/special_theme', lightblog_views.publish_special_theme),
    # 下架专题
    path('api/down/special_theme', lightblog_views.down_special_theme),

    # 获取个人专栏
    path('api/get/personal_column', personalColumn.get_column),
    # 新增个人专栏
    path('api/add/personal_column', personalColumn.add_column),
    # 获取个人专栏详情
    path('api/detail/personal_column', personalColumn.column_detail),
    # 更新个人专栏
    path('api/update/personal_column', personalColumn.update_column),
    # 删除个人专栏
    path('api/del/personal_column', personalColumn.del_column),

    # 获取用户文章
    path('api/get/articlelist', articleViews.get_articles),
    # 获取专题和专栏的数据
    path('api/get/columnTheme', articleViews.get_column_theme),
    # 发布文章
    path('api/publish/article', articleViews.publish_article),
    # 获取文章详情编辑
    path('api/detail/article', articleViews.detail_article),
    # 编辑文章
    path('api/update/article', articleViews.update_article),
    # 上传图片
    path('api/upload/image', articleViews.upload_articleImg),
    # 申请发布文章
    path('api/apply/article',articleViews.applyShowArticle),
    # 删除文章
    path('api/del/article', articleViews.del_article),

    # admin 文章获取
    path('api/admin/get/articlelist', articleViews.get_all_article),

]