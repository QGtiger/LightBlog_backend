from django.shortcuts import HttpResponse
import jwt
from django.conf import settings
import json
import re


try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object

# 拦截器
class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path != '/account/login' and request.path != '/account/register' and bool(re.match('^/admin.*?', request.path)) != True and bool(re.match('^/static.*?', request.path)) != True and bool(re.match('^/media.*?', request.path)) != True:
            token = request.META.get('HTTP_AUTHORIZATION')
            if token:
                pass
            else:
                return HttpResponse(json.dumps({'tips': '您未登录', 'status':402,"success": False}))
            try:
                dict = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                username = dict.get('data').get('username')
            except jwt.ExpiredSignatureError:
                return HttpResponse(json.dumps({"status": 401, "tips": "Token expired","success": False}))
            except jwt.InvalidTokenError:
                return HttpResponse(json.dumps({"status": 401, "tips": "Invalid token","success": False}))
            except Exception as e:
                return HttpResponse(json.dumps({"status": 401, "tips": "Invalid token","success": False}))