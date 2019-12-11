from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe

# Register your models here.
@admin.register(ArticleColumn)
class ArticleColumnAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'column', 'created']
    list_filter = ('user',)
    search_fields = ('user__username', 'column',)


@admin.register(ArticlePost)
class ArticlePostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'column', 'created', 'updated']
    list_filter = ('author__username', 'title', )
    search_fields = ('id', 'author__username', 'title', )


@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'imageShow']
    readonly_fields = ('imageShow',)

    def imageShow(self, obj):
        return mark_safe(
            u'<img src="%s" width="130px">' %
            obj.image_130x56.url)
    # 页面显示字段名称
    imageShow.short_desscription = u'头像'
