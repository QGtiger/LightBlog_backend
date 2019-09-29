from django.contrib import admin
from .models import BlogArticle

# Register your models here.
#admin.site.register(BlogArticle)
admin.site.site_title="LightBlog 管理"
admin.site.site_header="LightBlog"

@admin.register(BlogArticle)
class BlogArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publish")
    list_filter = ("publish", "author")
    search_fields = ("title", "body")
    date_hierarchy = "publish"
    ordering = ["publish", "author"]