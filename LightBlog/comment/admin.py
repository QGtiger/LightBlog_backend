from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Comment_reply)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment_reply', 'reply_type', 'comment_user', 'created', 'reply_comment', 'is_read']
    list_filter = ('comment_user__username',)
    search_fields = ['id', 'comment_user__username', 'comment_reply__article__title']

