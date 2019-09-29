from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # 聊天室
    path('',views.chat, name='chat'),
]