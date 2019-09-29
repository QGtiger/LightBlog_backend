from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe


# Register your models here.
@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'user',
        'school',
        'company',
        'profession',
        'address',
        'aboutme',
        'photo_img']
    list_filter = ('school', )
    search_fields = ['user__username', 'school', ]
    readonly_fields = ('photo_img',)

    def photo_img(self, obj):
        return mark_safe(
            u'<img src="%s" width="100px">' %
            obj.photo_100x100.url)

    # 页面显示字段名称
    photo_img.short_desscription = u'头像'
