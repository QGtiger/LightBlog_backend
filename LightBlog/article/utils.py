import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, HttpResponse
import json


def is_superuser(func):
    def wrapper(request,*args,**kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        if not user.is_superuser:
            return HttpResponse(json.dumps({"success": False, 'tips': "您没有权限"}))
        return func(request,*args,**kwargs)
    return wrapper


def get_user(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    username = dict.get('data').get('username')
    user = User.objects.get(username=username)
    return user


def log_in(func):
    '''身份认证装饰器，
    :param func:
    :return:
    '''
    def wrapper(request,*args,**kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = dict.get('data').get('username')
        user = User.objects.get(username=username)
        if not user.is_superuser:
            return HttpResponse(json.dumps({"success": False, 'tips': "您没有权限"}))
        return  func(request,*args, **kwargs)
    return wrapper