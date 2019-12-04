from django.urls import path
from . import views
from . import lightblog_views

# 一定要写这行，否则html中会报 is not a  registered namespace 错误
app_name = 'account'

urlpatterns = [
    # 登录
    path(r'login', views.account_login,name='account_login'),
    # 登出
    path(r'logout/', views.account_logout,name='account_logout'),
    # 注册
    path(r'register',views.account_register,name='account_register'),
    # 密码重置
    path(r'setpassword/',views.account_setpassword,name='account_setpassword'),

    # 是否登录
    path(r'islogin', views.account_islogin, name="account_islogin"),

    # 个人信息查询
    path(r'myinformation/',views.myself,name='my_information'),
    # 个人信息编辑
    path(r'edit_myself/',views.myself_edit,name='edit_myself'),
    # 个人图片上传
    path(r'my-image/', views.my_image, name="my_image"),
    # 获取头像API
    path(r'get_avator/',views.get_avator, name='get_avator'),
    # 用户信息查询
    path(r'author/<path:username>', views.author_info, name='author_info'),
    # 个人信息中心的博客文章的流加载
    path(r'article_page/<path:username>', views.article_page, name="article_page"),
    # 个人喜欢的文章
    path(r'article_like/<path:username>', views.article_like, name="article_like"),

    # 上传头像
    path(r'api/upload/avator', lightblog_views.upload_avator),
    # 上传 用户背景
    path(r'api/upload/author_bg', lightblog_views.upload_author_background),
    # 获取用户详细信息
    path(r'api/detail/author', lightblog_views.detail_author),
    # 获取用户文章，推荐、发布、点赞文章
    path(r'api/get/blogs', lightblog_views.get_author_blog),

    # 关注或者取消关注
    path(r'api/author/follow', lightblog_views.follow_author),
    # ta关注的人
    path('api/list/follow', lightblog_views.follow_list),
]